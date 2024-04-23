import streamlit as st
import serpapi
from serpapi import GoogleSearch
import requests  # For fetching and parsing the retrieved webpage (optional)
from bs4 import BeautifulSoup  # For parsing HTML (optional)
from dotenv import load_dotenv  # For loading environment variables
import os

# Load environment variables from .env file (optional)
# load_dotenv()

def get_patent_info(patent_id):
  """
  Searches Google Patents for the given patent ID using SerpApi.
  Optionally fetches and parses the retrieved webpage to extract basic information.

  Args:
      patent_id: The ID of the patent to search for.

  Returns:
      A dictionary containing the patent title, inventors, and assignee (if found).
  """

  # Retrieve SerpApi key from environment variable (replace with your variable name)
  serpapi_key = os.getenv("5f56d818c8546b71cf0abe3e779ffdf91e8143cab8cf057717cba03525001c14")

  # Define the search query (replace 'en' with your preferred language code)
  query = f"patent {patent_id} (en)"

  # Use SerpApi to search Google Patents
  search = GoogleSearch(api_key = serpapi_key)
  params = {
      "engine": "google_patents",
      "q": query,
  }
  results = search.search(params)

  # Extract the URL of the top search result
  if results.get("organic_results"):
    patent_url = results["organic_results"][0]["link"]
  else:
    return None

  # Optional: Fetch and parse the retrieved webpage to extract information
  try:
    response = requests.get(patent_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract title, inventors, and assignee (replace selectors as needed)
    title_element = soup.find('h1', class_='ipc-section-header__title')
    inventors_element = soup.find('ul', class_='inventors-list')  # Adjust selector based on website structure
    assignee_element = soup.find('div', class_='assignee-holder')  # Adjust selector based on website structure

    if title_element:
      title = title_element.text.strip()
    else:
      title = None
    if inventors_element:
      inventors = ", ".join([inventor.text.strip() for inventor in inventors_element.find_all('li')])
    else:
      inventors = None
    if assignee_element:
      assignee = assignee_element.find('span', class_='party-name').text.strip()
    else:
      assignee = None

    return {
      "title": title,
      "inventors": inventors,
      "assignee": assignee,
    }
  except Exception as e:
    st.error(f"Error fetching and parsing patent webpage: {e}")
    return None

def main():
  """Streamlit app for patent search and basic information retrieval."""

  st.set_page_config(page_title="Patent Search and Information")
  st.header("Find a Patent and Get Basic Info")

  # Input field for patent ID
  patent_id = st.text_input("Enter Patent ID:")

  # Submit button to trigger search
  if st.button("Search Patent"):
    if patent_id:
      # Search for the patent using SerpApi
      patent_info = get_patent_info(patent_id)

      if patent_info:
        st.success(f"Patent ID '{patent_id}' Found!")
        # Display retrieved information
        st.write("Title:", patent_info["title"])
        st.write("Inventors:", patent_info["inventors"])
        st.write("Assignee:", patent_info["assignee"])
        # Optionally display a link to the retrieved patent page
        st.write("See full patent:",    ["organic_results"][0]["link"])
      else:
        st.warning(f"Patent ID '{patent_id}' not found on Google Patents.")
    else:
      st.warning("Please enter a patent ID to search.")

if __name__ == "__main__":
  main()
