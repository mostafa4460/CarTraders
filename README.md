API: https://developers.google.com/maps/documentation/javascript/places-autocomplete
Schemas: https://drawsql.app/springboard-1/diagrams/cartraders

API will be implemented only on the client side, since there is no use for it on the server side ...
API is a location autocomplete widget, so users can easily select their locations.

****************
   Main Views
****************

1) /?location=&trading=&looking_for=
render either:
    a. Screen sized background image and a sign up button
    b. Home page with search bar for querying trades and all trades in user's state (if logged in) 
    can also render trades by location of city, state and/or car being traded string and/or car users are looking for string

2) /signup, /login
render signup / login forms

3) /<username>
render user profile with all user trades

5) /trades/<id>
render a single trade

6) /trades/new, POST
only logged in user: render create listing form

7) /trades/<id>/edit, POST
only logged in user and owner of the listing: render edit listing form

8) /trades/<id>/delete, POST
only logged in user and owner of the listing: delete listing