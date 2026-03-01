# nasa-app
A Flask App integrating the NASA Open API. This application allows for users to explore NASA's most recently updated earth and astronomy images. 

## Earth
This page uses the Earth Polychromatic Imaging Camera (EPIC) API to display images taken from space of Earth. The natural images and enhanced images taken on the most recent day are displayed. 

## Space
This page display NASA's Astronomy Picture of the Day (APOD) for the past 10 days, providing the image along with the image description. Keywords are extracted from the image descriptions by NLP using the PyTextRank library. These keywords are hyperlinked to the search results of the keyword within the NASA Image and Video Library, where users can further explore media relating to these keywords.


