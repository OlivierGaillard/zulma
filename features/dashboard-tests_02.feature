Feature: Total of sellings and balance


    Scenario: Total amount of selling, given one existing and payments closed
        Given There exists one selling of "120.50" which is "closed"
        When I make one selling of "20.00"
        Then the total of sellings must be "140.50"
        And  the quantity of sellings must be "2"


    Scenario: Total Sellings but existing not closed
        Given There exists one selling of "120.50" which is "pending"
        When I make one selling of "20.00"
        Then the total of sellings must be "20.00"
        And  the quantity of sellings must be "2"


    Scenario: Stock quantity is updated after selling
        Given There is one article "plate" with quantity "12"
        When  I make one selling with quantity "6" of "plate" for one amount of "50" and payments are "closed"
        Then  The stock quantity of "plate" must be "6"

    Scenario: Simple Login
        Given User "golivier" with password "behave" exist
        When  This user visit "/login/"
        Then  It is logged


    Scenario: Add to cart
        Given User "golivier" with password "behave" exist
        And There is one article "plate" with quantity "12"
        When  This user visit "/login/"
        And This user adds the article to its cart by visiting "/cart/add_item" with quantity "2"
        Then There exists one cart-item with quantity "2"

