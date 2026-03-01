# nasa-app
A Flask App integrating the NASA Open API. This application allows for users to explore NASA's most recently updated earth and astronomy images. 

### Earth
This page uses the Earth Polychromatic Imaging Camera (EPIC) API to display images taken from space of Earth. The natural images and enhanced images taken on the most recent day are displayed. 

### Space
This page display NASA's Astronomy Picture of the Day (APOD) for the past 10 days, providing the image along with the image description. Keywords are extracted from the image descriptions by NLP using the PyTextRank library. These keywords are hyperlinked to the search results of the keyword within the NASA Image and Video Library, where users can further explore media relating to these keywords.

## How to Use this Project
1. Clone the repository.
2. Set up a Python virtual environment.
3. Install the packages listed in requirements.txt.
4. Run the app. The app will start a local server which allows for the app to be viewed.

### License
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)


