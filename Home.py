import requests
from bs4 import BeautifulSoup
import pandas as pd
import config
import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

SCRAPERAPI = config.ScraperAPI

#APIKEY = SCRAPERAPI

HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
            AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/90.0.4430.212 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

def get_soup(url):
  payload = {'api_key': APIKEY, 'url': url}
  r = requests.get('http://api.scraperapi.com', params=payload)
  soup = BeautifulSoup(r.text, 'html.parser')
  return soup

def date_fixes(dfcopy):
  dfcopy['Date_Posted'] = dfcopy['Date_Posted'].replace({'Posted today': 1})
  dfcopy['Date_Posted'] = dfcopy['Date_Posted'].replace({'Just Posted': 1})
  dfcopy['Date_Posted'] = dfcopy['Date_Posted'].replace({'Urgently Hiring': 0})
  dfcopy['Date_Posted'] = dfcopy['Date_Posted'].str.replace(r'[^0-9]+', '')
  dfcopy['Date_Posted'] = dfcopy['Date_Posted'].fillna(-1)
  return dfcopy

Query = 'Data+Analyst'
State = 'WA'
City = 'Seattle'
Radius = '20'

#Remove number from start Url
def get_postings(pages):
  df = pd.DataFrame(columns=['Title', 'Description', 'Link'])
  base_link = 'https://www.indeed.com'
  #Set page range
  for number in range(0,pages*10,10):
    soup = get_soup(f'https://www.indeed.com/jobs?q={Query}&l={City}%2C+{State}&radius={Radius}&start={number}')
    entry = soup.find_all('td', class_='resultContent')
    print(number)
    for item in entry:
        #Job Title

        title = item.find(class_='jobTitle').text
        print(title)
        #Get specific posting link
        link = item.a['href']
        new_link = base_link + link
        print(new_link)
        #Retrieve Job Page (single) from Link
        soup = get_soup(new_link)
        #Retrieve Description
        try:
          description = soup.find(class_='jobsearch-jobDescriptionText').get_text()
        except:
          description=''
          continue
        df.loc[len(df.index)] = [title, description, new_link]
        #Fix Dates
        #df = date_fixes(df)
  return df

#Streamlit App
st.title('Indeed Job Search Results to CSV')

#Please make an api key at https://www.scraperapi.com/
st.markdown('''
### Please make an api key at https://www.scraperapi.com/
''')


#Sidebar with disclamer
st.sidebar.title('Disclaimer')
#disclamer
st.sidebar.markdown('''
This app is for educational purposes only.
Use is at your own risk and subject to Indeed's Terms of Service and ScaperAPI's Terms of Service.
''')

st.sidebar.subheader('About')
st.sidebar.markdown('''
Results will be different than in browser due to the use of a api''')

#Request user input for scraper api key
APIKEY = st.text_input('Scraper API Key')

# Request user input for number of pages to scrape
pages = st.sidebar.number_input('Number of Pages to Scrape', min_value=1, max_value=10, value=1, step=1)
#Request user input for Query, State, City and Radius
Query = st.sidebar.text_input('Query (No Special Characters)', 'Data Analyst')
#Replace whitespace with + for Query
Query = Query.replace(' ', '+')
State = st.sidebar.text_input('State Code', 'WA')
City = st.sidebar.text_input('City', 'Seattle')
Radius = st.sidebar.text_input('Search Radius', '20')

#Run get_postings function when button is clicked
if st.button('Search'):
  df = get_postings(pages)
  csv = df.to_csv().encode('utf-8')
  st.dataframe(df)
  
#Download df as csv when button is clicked
st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='jobsearch.csv',
    mime='text/csv',
)
  




# #Upate wordcloud when button is clicked
if st.button('Update Wordcloud'):
    # create the word map using the code from the previous answer
    word_map = df['Description'].str.split(expand=True).stack().value_counts().to_dict()
    
    # remove stopwords from the word map using the English stopwords corpus
    stop_words = set(stopwords.words('english'))
    word_map = {word: freq for word, freq in word_map.items() if word.lower() not in stop_words}
    
    # create the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_map)
    
    # display the word cloud
    plt.figure(figsize=(12,6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

