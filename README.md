***
# Car-Traderz ([website](https://car-traderz.herokuapp.com/))
***

**This website connects users who enjoy trading and owning different cars, without the hassle of dealing with selling and buying. Instead of using platforms typically known for selling/buying items, car enthusiasts now have a dedicated platform where the main objective of every user is to trade vehicles.**

### As a user, you can:

1. Create a free account or log in with an existing account.
2. Edit/Delete your own profile (including contact info and location).
3. Make a new trade consisting of:
	* Car you are trading (title)
	* Car you are looking for
	* An image URL of your car
	* Additional $$$, if asking
	* Offering $$$, if offering
	* A trade description
4. Edit/Delete own trades only.
5. Search for trades by location, car being traded, and car wanted (by default, if the user does not use the search bar, the most recent 100 trades located in the user's state will be retrieved and displayed).

### The standard user flow will typically look like this:

1. Sign up for a free account.
2. Create a trade for the car you currently own to have other users reach out to you with different offers.
3. Use the search bar to look for trades requesting the car you own (leaving the location search bar empty, which will default to trades within your own state).
4. If there are a lot of trades asking for your specific vehicle, you may then want to narrow the search even further by including the city you are located in and/or the car that you are asking for as well.
5. This will narrow the choices to the closest user near you, who is trading the car you are looking for and asking for the car you currently own.

### Important Note

There are certain requirements for the user location input to be accepted and then stored into the database. Therefore, Google's Places Autocomplete API was used to auto-suggest locations based on the users' input by CITY, STATE only. The API was specifically restricted to auto-suggest only cities, states in the U.S to prevent users from inputting their full addresses. Read more about the API
[here](https://developers.google.com/maps/documentation/javascript/places-autocomplete).

## Stack Used:
**Python  
Flask  
Postgresql     
JavaScript** (for the API)  
**HTML  
CSS**
