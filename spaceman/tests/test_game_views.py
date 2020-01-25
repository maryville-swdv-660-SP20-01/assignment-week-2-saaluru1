from django.test import TestCase
from unittest.mock import *
from rest_framework.test import APIRequestFactory

from game_api.views import *
from game_api.models import Game

import json
from django.http.request import HttpRequest

class GameApiViewTests( TestCase ):

    def setUp( self ):
        self.expected_game_data = {
            'guesses_allowed': 5,
            'guesses_taken': 3,
            'letters_guessed': ['A'],
            'guessed_word_state': ['', 'A'],
            'is_game_over': False,
            'id': None
        }

        self.mock_game = Game(
                word = "TESTWORD",
                guesses_allowed = self.expected_game_data['guesses_allowed'],
                guesses_taken = self.expected_game_data['guesses_taken'],
                letters_guessed = self.expected_game_data['letters_guessed'],
                guessed_word_state = self.expected_game_data['guessed_word_state'],
                is_game_over = self.expected_game_data['is_game_over']
            )

        self.request_factory = APIRequestFactory()
        self.mock_get_request = self.request_factory.get('dummy')


    ### POST (create game) view
    def test_game_view_should_create_new_game_on_POST( self ):
        response = game_view( self.request_factory.post('dummy') )

        self.assertEquals( response.status_code, 200)
        self.assertIsNotNone( response.data['id'] )
        self.assertTrue( response.data['id'] >= 0 )
        
    ### PUT (guess letter) view 
    def test_game_view_should_create_update_guesses_on_PUT( self ):
        with patch.object( Game.objects, 'get' ) as mock_get:
            self.mock_game.letters_available = ['B','C']
            mock_get.return_value = self.mock_game

            mock_request = self.request_factory.put( 'dummy', json.dumps({'letters_guessed': ['B']}), content_type='application/json')

            response = game_view( mock_request, 25 )
            
            mock_get.assert_called_with( pk=25 )
            self.assertEquals( response.status_code, 200 )
            self.assertEquals( response.data['letters_guessed'], ['A','B'])

    def test_game_view_should_reject_PUT_if_invalid( self ):
        with patch.object( Game.objects, 'get' ) as mock_get:
            self.mock_game.letters_available = ['B','C']
            mock_get.return_value = self.mock_game

            mock_request = self.request_factory.put( 'dummy', json.dumps({'letters_guessed': ['A']}), content_type='application/json')

            response = game_view( mock_request, 25 )
            
            mock_get.assert_called_with( pk=25 )
            self.assertEquals( response.status_code, 400 )


    ### GET solution view
    # TODO: Add tests for Getting a game's solution
    # HINT: remember the `setUp` fixture that is in this test class, 
    #   it constructs things that might be useful
    """ We are missing tests for the solution response for the Game view/controller. The expectations are that the get_solution function should:
    1. respond with a 404 status code when the id for a game is not found
    2. respond with a game's solution word in a json structure like this:
    {
        "solution": "batman"
    }
    HINT: you're going to need to mock whatever does the game object look up """
    
    def test_game_view_game_solution_for_game_is_not_found( self ):
        with patch.object( Game.objects, 'get' ) as mock_get:
            mock_get.return_value = self.mock_game
            mock_get.side_effect = Game.DoesNotExist
            response = game_solution(self.mock_get_request,25)
            self.assertEquals( response.status_code, 404)

    def test_game_view_game_solution_for_word( self ):
        with patch.object( Game.objects, 'get' ) as mock_get:
            # Changing the word
            self.mock_game.word = 'batman'
            mock_get.return_value = self.mock_game
            response = game_solution(self.mock_get_request,25)
            self.assertEquals( response.status_code, 200)
            self.assertEquals(response.data , {'solution': 'batman'})
