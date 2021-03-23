API: https://developers.google.com/maps/documentation/javascript/places-autocomplete
Schemas: https://drawsql.app/springboard-1/diagrams/cartraders

API will be implemented only on the client side, since there is no use for it on the server side ...
API is a location autocomplete widget, so users can easily select their locations.

****************
   Main Views
****************

1) /
render either:
    a. Screen sized background image and a sign up button
    b. Home page with search bar for querying listings (if logged in)

2) /signup, /login
render signup / login forms

3) /<username>
render user profile with all user listings

4) /listings?location=&trading=&looking_for=
    a. render all listings in the current user's state by default OR
    b. render listings by location of city, state and/or car being traded string and/or car users are looking for string

5) /listings/<id>
render a single listing

6) /listings/create, POST
only logged in user: render create listing form

7) /listings/<id>/edit, POST
only logged in user and owner of the listing: render edit listing form

8) /listings/<id>/delete, POST
only logged in user and owner of the listing: delete listing