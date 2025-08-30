from merlin import Merlin
from openrouterwrapper import OpenrouterWrapper
import time

system_prompt = open('sysprompt.txt', 'r').read()
api_key = open('openrouterkey-1.txt', 'r').read().strip()
model = "moonshotai/kimi-k2:free"


merlin = Merlin(headless=False)
wrapper = OpenrouterWrapper(
	model=model,
	user_credentials=api_key,
	system_prompt=system_prompt
)


def play_game(model, system_prompt, api_key, max_messages = 10): # You may want max_messages to be higher for level 7
	for level in range(1,8):
		# We clear the context for each new level
		merlin_message = 'Hello traveler! Ask me anything...'
		wrapper.clear_history(keep_system=True)
		bad_password = False
		print(f'Trying to solve level {level}')

		# Dialogue loop
		for i in range(max_messages):
			agent_message = wrapper.send_message(merlin_message)

			# Basic tool call
			if 'Merlin:' in agent_message:
				merlin_message = merlin.message(agent_message.split('Merlin: ')[-1])
			elif 'Password:' in agent_message:
				password_result = merlin.guess_password(agent_message.split('Password: ')[-1])
				if password_result:
					print(f'Successfully Completed Level {level}!\n')
					break
				else:
					merlin_message = 'Alas! That password is incorrect!'
			else:
				print(f'!! Invalid Tool Call !! \n{agent_message}\n')

			# Abort if max messages is reached
			if i + 1 == max_messages:
				print(f'{model} got to level {level}.')
				return

play_game(model, system_prompt, api_key, max_messages=25)
merlin.close() 
