import json
import re
from sympy import use
import wikipedia
import random
import time
import sys
import streamlit as st
import streamlit.components.v1 as components
from dataclasses import dataclass
from streamlit_pills import pills
from streamlit_searchbox import st_searchbox
from faker import Faker
import requests
from bs4 import BeautifulSoup

sys.path.append('./backend/utils')
sys.path.append('./backend/indexer')

from PositionalIndex import PositionalIndex
from SpellChecker import SpellChecker

fake = Faker()

# Load indexer
indexer = PositionalIndex()
#indexer.load_index('../backend/database/index/index_base.txt')
spell_checker = SpellChecker(use_secondary=True) 

@dataclass
class SearchResult:
    title: str
    description: str
    link: str
    image: str  # Image URL
    
def get_news(doc_id):
    url = "http://ttds.martinnn.com:5002/api/news/{}".format(doc_id)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def make_results(metadata):
    results = []
    for date, title in metadata:
        link = fake.url()
        image = fake.image_url(width=50, height=50)  
        results.append(SearchResult(title=title, description=date, link=link, image=image))
    return results

def display_search_results(metadata, query, correction=''):
    # Style configuration
    title_color = '#0000EE' 
    font_family = 'Arial' 
    font_size = '16px' 
    if correction != query:
        if st.button(f"Did you mean: :blue[**_{correction}_**]?"):
            query = correction
    st.markdown(f"<span style='font-size: 100%; color: gray'>Showing results for: <span style='color: blue'><b><i>'{query}'</i></b></span></span>", unsafe_allow_html=True)
    results = make_results(metadata)
    st.caption(f"Found {len(results)} results.")
    for result in results:
        print(result)
        st.markdown(f"""
        <div style="display: flex; align-items: center; padding: 10px; margin: 10px 0; border-radius: 10px; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);">
            <img src="{result.image}" alt="{result.title}" style="width: 50px; height: 50px; border-radius: 50%; margin-right: 10px;">
            <div style="flex-grow: 1;">
                <h4 style="margin: 0; color: {title_color}; font-family: {font_family}; font-size: {font_size};">
                    <a href="{result.link}" target="_blank" style="text-decoration: none; color: {title_color};">{result.title}</a>
                </h4>
                <a href="{result.link}" target="_blank" style="text-decoration: none; color: grey;">{result.link}</a>
                <p style="color: grey; font-family: {font_family}; font-size: {font_size};">{result.description}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    

#search_wikipedia = lambda searchterm: [searchterm] + wikipedia.search(searchterm) if searchterm else [searchterm]
search_wikipedia = lambda searchterm: [searchterm] if searchterm else [searchterm]

# Set page config
st.set_page_config(page_title="Search Engine with Timeline", layout="wide")


#with open('example.json', "r") as f:
#    timeline_data = f.read()


#data = json.dumps(timeline_data)
    

def timeline(data, height=800):

    """Create a new timeline component.

    Parameters
    ----------
    data: str or dict
        String or dict in the timeline json format: https://timeline.knightlab.com/docs/json-format.html
    height: int or None
        Height of the timeline in px

    Returns
    -------
    static_component: Boolean
        Returns a static component with a timeline
    """

    # if string then to json
    if isinstance(data, str):
        data = json.loads(data)

    # json to string
    json_text = json.dumps(data) 

    # load json
    source_param = 'timeline_json'
    source_block = f'var {source_param} = {json_text};'

    # load css + js
    cdn_path = 'https://cdn.knightlab.com/libs/timeline3/latest'
    css_block = f'<link title="timeline-styles" rel="stylesheet" href="{cdn_path}/css/timeline.css">'
    js_block  = f'<script src="{cdn_path}/js/timeline.js"></script>'


    # write html block
    htmlcode = css_block + ''' 
    ''' + js_block + '''

        <div id='timeline-embed' style="width: 95%; height: '''+str(height)+'''px; margin: 1px;"></div>

        <script type="text/javascript">
            var additionalOptions = {
                start_at_end: false, is_embed:false,
            }
            '''+source_block+'''
            timeline = new TL.Timeline('timeline-embed', '''+source_param+''', additionalOptions);
        </script>'''


    # return rendered html
    static_component = components.html(htmlcode, height=height)

    return static_component

#timeline(timeline_data, height=320)

# Initialize query in session state
if 'query' not in st.session_state:
    st.session_state['query'] = ''
    
if 'selected_pills' not in st.session_state:
    st.session_state['selected_pills'] = []

col1, col2, col3 = st.columns([1,4,1])

with col1:
    st.subheader("Timeline")

with col2:
    st.subheader("Search")
    query = st.text_input(label="Search", value=st.session_state['query'])
    
    if st.button("Search", use_container_width=True) or query:
        correction = spell_checker.check_and_correct(query)
        returned_docs = indexer.process_query(correction)
        metadata = []
        for doc_id, positions in returned_docs:
            article = get_news(1) # Change '1' to doc_id when index is synced with db
            all_tags = article.find_all('p')
            date = all_tags[0].text
            title = all_tags[1].text
            content = all_tags[2].text # Need to add this later
            metadata.append((date, title))
        display_search_results(metadata, query, correction=correction)
        st.session_state['selected_pills'] = []

with col3:
    st.container()
    st.subheader("NER")

    pill_options = [fake.word() for _ in range(5)] 
    pill_icons = ["🍀", "🎈", "🌈", "🔥", "🌟"] 

    # Display pills and get the selected pill
    selected_pill = pills("Filter by:", pill_options, pill_icons)
    
    st.write(f"You selected: {selected_pill}")
    
    




