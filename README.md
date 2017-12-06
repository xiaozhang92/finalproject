## Aparkment

A website that lets a developer or investor find and estimate the total value of residential units transformed from parking
facilities in Manhattan, New York City. You are able to locate parking facilities in Manhattan and get information about gross floor
area. You can input types of living units desired at different percentages, and receive a total number of units transformed from
selected parking facilities. Average values are collected and calculated with your input to generate a total value of the
transformed residential units.

# CONFIGURING

Similar to the problem Mashup, we are using Google API to get access to the map. In order to implement the web application, you have to
get an API key at first. (reference : https://docs.cs50.net/2017/fall/psets/8/mashup/mashup.html#distribution)
1. Visit developers.google.com/maps/web/, logging in if prompted, and click GET A KEY at top-right.
2. Click Select or create project, click +Create a new project, and input something under Enter new project name.
3. Click CREATE AND ENABLE API.
4. Highlight and copy the value below YOUR API KEY.
5. In a terminal window, execute: export API_KEY=value
   where value is that (pasted) value, without any space immediately before or after the =


# SEARCH

An input of an address or postal code for a parking facility you are looking for, the map will zoom in to the area and show all
parking facilities within the frame.


# MAP and MARKERS

One parking facility could be selected by clicking on the marker, information of the clicked facility would show up.


# CONVERT

The button is to lead you to next page for further input for calculation. It is login required, so you can have a history all the
searches and calculations for future access privately.


# REGISTER

If you not yet have an account, this is where you register.


# HISTORY

Under the account you are logged in, you can access a history of all searches and calculations you did in the past.


# LOG IN

Logging into your account so you can continue to do conversion calculation and access your history of searches and calculations.


# LOG OUT

Logging out from your account.
