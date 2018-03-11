import math

from config import MEN_WIN_SCORE, MEN_FORFEIT_SCORE, WOMEN_WIN_SCORE, WOMEN_FORFEIT_SCORE, MAX_ROUNDS
from hash_table import HashTable
from linked_list import List
from match import Track, Match
from user_input import next_gender, next_bool, next_input_type, FILE, next_string, MALE


class TournamentType:
    def __init__(self, name: str, prizes: HashTable, difficulty: float):
        self.name = name
        self.prizes = prizes
        self.difficulty = difficulty


class Tournament:
    def __init__(self, tournament_type: TournamentType, season, previous, complete, men_round, women_round,
                 men_stats=HashTable(), women_stats=HashTable()):
        self.type = tournament_type
        self.season = season
        self.previous = previous
        self.complete = complete
        self.men_track = Track('men', men_round, men_stats, men_stats.clone(), MEN_WIN_SCORE, MEN_FORFEIT_SCORE)
        self.women_track = Track('women', women_round, women_stats, women_stats.clone(), WOMEN_WIN_SCORE,
                                 WOMEN_FORFEIT_SCORE)

    def run(self):
        running = True

        while running:
            gender = next_gender('Select the track to play for the next round')

            track = self.men_track if gender == MALE else self.women_track
            self.play_track(track)

            running = next_bool('Would you like to start the next round?', True)

    def play_track(self, context):
        if context.round > MAX_ROUNDS:
            print('This track is already complete')
            return

        print('Playing the %s\'s track' % context.name)
        input_type = next_input_type('How should data be entered?')
        winners = HashTable()
        winner = None
        matches = List()

        if input_type == FILE:
            # Get the file to load the round data from.
            default_round_file = '../resources/%s/%s/%s/round_%d.csv' % \
                                 (self.season.name, self.type.name.lower(), context.name, context.round)
            round_file = next_string('Enter file for round %d' % context.round, default_round_file)
            from loader import load_round
            matches = load_round(round_file, context)
        else:
            match_count = int(math.pow(2, MAX_ROUNDS - context.round))

            for i in range(0, match_count):
                match = Match(context)
                matches.append(match)

        # Run each match.
        for match in matches:
            # Find the winner and add them to the next batch.
            winner, winner_score, loser, loser_score = match.run(context.winning_score, context.remaining)
            winners.insert(winner.player.name, winner)

            # Update the winner profile.
            winner.win()
            winner.add_score(winner_score, loser_score)

            # Update the loser profile.
            loser.loss()
            loser.add_score(loser_score, winner_score)

        if context.round == MAX_ROUNDS:
            print('Tournament %s successfully complete for the men\'s track' % self.type.name)
            print('Winner: %s' % winner.player.name)
            context.round += 1
            return

        print('Winners for round %d:' % context.round)

        for name, stats in winners:
            print('- %s' % name)

        context.remaining = winners
        context.round += 1
