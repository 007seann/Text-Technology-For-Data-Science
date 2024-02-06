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

sys.path.append('../backend/utils')
from SpellChecker import SpellChecker

spell_checker = SpellChecker(use_secondary=True) 

fake = Faker()

@dataclass
class SearchResult:
    title: str
    description: str
    link: str
    image: str  # Image URL

def generate_fake_results(num_results):
    results = []
    for _ in range(num_results):
        title = fake.sentence(nb_words=6)
        description = fake.text(max_nb_chars=200)
        link = fake.url()
        image = fake.image_url(width=50, height=50)  
        results.append(SearchResult(title=title, description=description, link=link, image=image))
    return results

def display_search_results(results, query, correction=''):
    # Style configuration
    title_color = '#0000EE' 
    font_family = 'Arial' 
    font_size = '16px' 
    if correction != query:
        if st.button(f"Did you mean: :blue[**_{correction}_**]?"):
            results = generate_fake_results(num_results)
            query = correction
    st.markdown(f"<span style='font-size: 100%; color: gray'>Showing results for: <span style='color: blue'><b><i>'{query}'</i></b></span></span>", unsafe_allow_html=True)
    st.caption(f"Found {len(results)} results.")
    for result in results:

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
    
    

search_wikipedia = lambda searchterm: [searchterm] + wikipedia.search(searchterm) if searchterm else [searchterm]

# Set page config
st.set_page_config(page_title="Search Engine with Timeline", layout="wide")

num_results = 8

results = generate_fake_results(num_results)


with open('example.json', "r") as f:
    timeline_data = f.read()


data = json.dumps(timeline_data)
    

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

timeline(timeline_data, height=320)

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
    query = st_searchbox(search_wikipedia, placeholder="Search..", clear_on_submit=False, rerun_on_update=True) 
    
    if st.button("Search", use_container_width=True) or query:
        correction = spell_checker.check_and_correct(query)
        display_search_results(results, query, correction=correction)
        st.session_state['selected_pills'] = []

with col3:
    st.container()
    st.subheader("NER")

    pill_options = [fake.word() for _ in range(5)] 
    pill_icons = ["🍀", "🎈", "🌈", "🔥", "🌟"] 

    # Display pills and get the selected pill
    selected_pill = pills("Filter by:", pill_options, pill_icons)
    
    st.write(f"You selected: {selected_pill}")
    
    

