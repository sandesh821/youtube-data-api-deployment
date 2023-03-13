from flask import Flask, render_template, request
import googleapiclient.discovery
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import json 
from dotenv import load_dotenv
import os
import io
import base64
import matplotlib
matplotlib.use('Agg')



app = Flask(__name__)

class Youtube_Data_API:
      def __init__(self, channel_id):
            #Load the API key from environment variable
            load_dotenv()
            self.api_key = os.getenv('api_key')
            # set the channel IDs
            self.channel_id = channel_id
            #create the youtube API client object
            self.youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=self.api_key )


      def get_channel_data(self):
            # Make the Request to youtube API and get response as channel details
            all_data = []
            self.request = self.youtube.channels().list(
            part='snippet,contentDetails,statistics',
            id=','.join(self.channel_id)
            )
            # Response in json format
            response = self.request.execute()
            # print(json.dumps(response,indent=2))
            
            # From response extract the channel name, SubscriberCount, viewCount
            for i in range(len(response['items'])):
                  data = dict(channel_name = response['items'][i]['snippet']['title'],
                              SubscriberCount = response['items'][i]['statistics']['subscriberCount'],
                              viewCount = response['items'][i]['statistics']['viewCount']
                              )
                  all_data.append(data)
            #Return the data as the list of dictionaries
            return all_data
      

      def save_to_csv(self, channel_Data):
            # Convert Data to Pandas Dataframe and save it as 'Youtube_data.csv' file
            df = pd.DataFrame.from_dict(channel_Data)
            df.to_csv('Youtube_data.csv')
            

      def plot_subscriber_count(self, channel_data):
            # Plot the bar chart for subscriber count for each youtube channel
            plt.clf()
            df = pd.DataFrame.from_dict(channel_data)
            df['SubscriberCount'] = pd.to_numeric(df['SubscriberCount'])
            sns.set(rc={'figure.figsize':(8,5)})
            sns.barplot(x='channel_name',y='SubscriberCount',data=df)
            plt.title('YouTube Channel Subscriber Counts')
            plt.xlabel('Channel Name')
            plt.ylabel('Subscriber Count')

      def plot_view_count(self, channel_data):
            #Plot the bar chart of view count for each youtube channel
            plt.clf()
            df = pd.DataFrame.from_dict(channel_data)
            df['viewCount'] = pd.to_numeric(df['viewCount'])
            sns.set(rc={'figure.figsize':(8,5)})
            sns.barplot(x='channel_name',y='viewCount',data=df)
            plt.title('YouTube Channel View Count')
            plt.xlabel('Channel Name')
            plt.ylabel('View Count')
            


@app.route('/', methods=['GET'])
def home():
      return render_template('home.html')



@app.route('/', methods=['POST'])
def get_channel_data():
      # Get input as channel IDs from user.
      channel_id = request.form.get('channel_ids')
      channel_id = list(map(str,channel_id.split()))
      
      # create object for Youtube_Data_API
      obj = Youtube_Data_API(channel_id)
      
      
      try:
            #get channel data from youtube API by using calling (call getResponse using class object)
            channel_Data = obj.get_channel_data()
      except:
            return render_template('error.html', message="channel id not correct: {}".format(channel_id))
      # save the channel data to csv file   
      obj.save_to_csv(channel_Data)

      # create dictionary to map the input to class methods
      method_dict = {
            "subscriber_count": obj.plot_subscriber_count,
            "view_count": obj.plot_view_count
            }     
      # take input from user (view_count or subscriber_count)
      user_input = request.form.get('chart_type')
      
      try:
            # Call the appropriate method based on the user input
            method_dict[user_input](channel_Data)
      except KeyError:
            # the error template if user input is not a valid key in the method dictionary
            return render_template('error.html', message="Error: {}".format(user_input))
      
      # Generate the PNG image of the chart ( create buffer memory and store image)
      buf = io.BytesIO()
      plt.savefig(buf, format='png')
      buf.seek(0)
      
      # Encode the PNG image as a base64 string
      img_data = base64.b64encode(buf.read()).decode('utf-8')
      # show  the results template with the chart image
      return render_template('results.html', chart_type=user_input, img_data=img_data)



if __name__ == '__main__':
      port = int(os.environ.get('PORT', 5000))
      app.run(host='0.0.0.0', port=port, debug=True)