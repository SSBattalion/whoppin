import random
import time
import requests
from highrise import BaseBot, Highrise, Position, AnchorPosition, Reaction
from highrise import __main__
from asyncio import run as arun
from emotes import Dance_Floor
import asyncio
from random import choice
import os
import json
from typing import List
from datetime import datetime, timedelta
from highrise.models import SessionMetadata
import re
from highrise.models import SessionMetadata,  GetMessagesRequest, User ,Item, Position, CurrencyItem, Reaction
from typing import Any, Dict, Union
from highrise.__main__ import *
import asyncio, random
from emotes import Emotes
from emotes import Dance_Floor
import contextlib

owners = ['alionardo_','bridewhoppin']
moderators = ['alionardo_','bridewhoppin']


class BotDefinition:


    def __init__(self, bot, room_id, api_token):
        self.bot = bot
        self.room_id = room_id
        self.api_token = api_token
        self.following_username = None

class Counter:
    bot_id = ""
    static_ctr = 0
    usernames = ['Alionardo_']

class Bot(BaseBot):
    continuous_emote_tasks: Dict[int, asyncio.Task[Any]] = {}  
    user_data: Dict[int, Dict[str, Any]] = {}
    continuous_emote_task = None
    cooldowns = {}  # Class-level variable to store cooldown timestamps
    emote_looping = False


    def __init__(self):
        super().__init__()
        self.load_temporary_vips()
        self.load_membership() 
        self.following_username = None
        self.maze_players = {}
        self.user_points = {}  # Dictionary to store user points
        self.current_trivia = None
        self.trivia_points = {}
        self.Emotes = Emotes
        self.emotesdf = Dance_Floor
        self.should_stop = False
        self.announce_task = None
        self.dancer = []  # Initialize dancer list
        self.owners =  ['alionardo_','bridewhoppin']  # List of owner usernames
        #conversation id var
        self.convo_id_registry = []
        #dance floor position
        min_x = 2.5
        max_x = 7.5
        min_y = 0
        max_y = 1
        min_z = 11.5
        max_z = 28.5
        self.dance_floor_pos = [(min_x, max_x, min_y, max_y, min_z, max_z)]

    async def teleport_user_to(self, target_username: str, position: Position, location_name: str):
        """Helper function to teleport users with feedback"""
        try:
            room_users = await self.highrise.get_room_users()
            target_id = None

            for room_user, _ in room_users.content:
                if room_user.username.lower() == target_username.lower():
                    target_id = room_user.id
                    break

            if target_id:
                await self.highrise.teleport(target_id, position)
                await self.highrise.chat(f"📍 Teleported @{target_username} to {location_name}")
            else:
                await self.highrise.chat(f"❌ User @{target_username} not found in room")
        except Exception as e:
            print(f"Teleport error: {e}")
            await self.highrise.chat("❌ Failed to teleport user")


        max_z = 17.5

        self.dance_floor_pos = [(min_x, max_x, min_y, max_y, min_z, max_z)]

        #dancer variable
        self.dancer = []

        #dance floor emotes var
        self.emotesdf = Dance_Floor
        #conversation id var
        self.convo_id_registry = []
        self.dance_floor_task = None

    def load_membership(self):
     try:
        with open("membership.json", "r") as file:
            self.membership = json.load(file)
     except FileNotFoundError:
        self.membership = []
    def save_membership(self):
     with open("membership.json", "w") as file:
        json.dump(self.membership, file)
    def load_temporary_vips(self):
        try:
            with open("temporary.json", "r") as file:
                self.temporary_vips = json.load(file)
        except FileNotFoundError:
            self.temporary_vips = {}

    def save_temporary_vips(self):
      with open("temporary.json", "w") as file:
          json.dump(self.temporary_vips, file)


    async def dance_floor(self):

        while True:

            try:
                if self.dance_floor_pos and self.dancer:
                    ran = random.randint(1, 73)
                    emote_text, emote_time = await self.get_emote_df(ran)
                    emote_time -= 1

                    tasks = [asyncio.create_task(self.highrise.send_emote(emote_text, user_id)) for user_id in self.dancer]

                    await asyncio.wait(tasks)

                    await asyncio.sleep(emote_time)

                await asyncio.sleep(1)

            except Exception as e:
                print(f"{e}")
    async def get_emote_df(self, target) -> None:

        try:
            emote_info = self.emotesdf.get(target)
            return emote_info      
        except ValueError:
            pass
    async def announce(self, user_input: str, message: str):
      while not self.should_stop:  
          await asyncio.sleep(6)
          await self.highrise.chat(user_input)
          await asyncio.sleep(60)
          await self.highrise.send_emote('emote-hello')

          if message.lower().startswith("-announce "):
              parts = message.split()
              if len(parts) >= 3:
                  user_input = message[len("-announce "):]
                  await self.announce(user_input, message)

    def stop_announce(self):
      self.should_stop = True
      if self.announce_task is not None:
          self.announce_task.cancel()

    async def start_announce(self, user_input: str, message: str):
      if self.announce_task is not None:
          return
      self.announce_task = asyncio.create_task(self.announce(user_input, message))

    async def on_start(self, session_metadata: SessionMetadata) -> None:
      try:
         Counter.bot_id = session_metadata.user_id
         print("Ali is booting ...") 
         self.dance_floor_task = asyncio.create_task(self.dance_floor())
         self.highrise.tg.create_task(self.highrise.walk_to(Position(16.5,0.5,1.5, facing='FrontRight')))
         self.load_temporary_vips()
         self.load_membership()
         await asyncio.sleep(15)
         await self.highrise.chat(f"Deployed")
         if Counter.bot_id not in self.dancer:
           self.dancer.append(Counter.bot_id)
      except Exception as e:
          print(f"An exception occured: {e}")  
    async def on_emote(self, user: User ,emote_id : str , receiver: User | None )-> None:
      print (f"{user.username} , {emote_id}")
    async def on_user_leave(self, user: User) -> None:
        if user.id in self.dancer:
                self.dancer.remove(user.id)
    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:

      try:
         await self.highrise.send_whisper(user.id, f"\nWelcome {user.username}!, If you have any questions or concerns ask a moderator, other than that enjoy the room! ❤️ 🌿")

      except Exception as e:
            print(f"An error on user_on_join: {e}")
    async def teleport_to(self, requester_user: User, target_username: str):
         room_users = await self.highrise.get_room_users()
         target_position = None

         for user, position in room_users.content:
            if user.username.lower() == target_username.lower(): 
                target_position = position
                break

         if target_position:
            new_position = Position(target_position.x, target_position.y, target_position.z, target_position.facing)
            await self.highrise.teleport(requester_user.id, new_position)

    async def teleport_user_next_to(self, target_username: str, requester_user: User):
      room_users = await self.highrise.get_room_users()
      requester_position = None

      for user, position in room_users.content:
        if user.id == requester_user.id:
            requester_position = position
            break
      for user, position in room_users.content:
        if user.username.lower() == target_username.lower(): 
          z = requester_position.z 
          new_z = z + 1 

          user_dict = {
            "id": user.id,
            "position": Position(requester_position.x, requester_position.y, new_z, requester_position.facing)
          }
          await self.highrise.teleport(user_dict["id"], user_dict["position"])



    async def run(self, room_id, token):
        definitions = [BotDefinition(self, room_id, token)]
        await __main__.main(definitions) 

    def remaining_time(self, username):
        if username in self.temporary_vips:
            remaining_seconds = self.temporary_vips[username] - int(time.time())
            if remaining_seconds > 0:
                return str(timedelta(seconds=remaining_seconds))
        return "Not a temporary VIP."


    async def on_chat(self, user: User, message: str) -> None:
      try:
         from fun_data import roasts, facts, pickup_lines
         import random

         if message.startswith("-promote"):
            if user.username.lower() not in self.owners:
                await self.highrise.chat("You do not have permission to use this command.")
                return
            parts = message.split()
            if len(parts) != 3:
                await self.highrise.chat("Usage: promote @username [moderator/designer]")
                return
            command, username, role = parts
            username = username.lstrip('@')

            if role.lower() not in ["moderator", "designer"]:
                await self.highrise.chat("Invalid role. Please use: moderator or designer")
                return

            room_users = await self.highrise.get_room_users()
            target_id = None
            for room_user, _ in room_users.content:
                if room_user.username.lower() == username.lower():
                    target_id = room_user.id
                    break

            if not target_id:
                await self.highrise.chat("User not found in room")
                return

            try:
                permissions = await self.highrise.get_room_privilege(target_id)
                setattr(permissions, role.lower(), True)
                await self.highrise.change_room_privilege(target_id, permissions)
                await self.highrise.chat(f"@{username} has been promoted to {role}")
            except Exception as e:
                await self.highrise.chat(f"Error: {e}")
                return

         if message.startswith("-demote"):
            if user.username.lower() not in self.owners:
                await self.highrise.chat("You do not have permission to use this command.")
                return
            parts = message.split()
            if len(parts) != 3:
                await self.highrise.chat("Usage: demote @username [moderator/designer]")
                return
            command, username, role = parts
            username = username.lstrip('@')

            if role.lower() not in ["moderator", "designer"]:
                await self.highrise.chat("Invalid role. Please use: moderator or designer")
                return

            room_users = await self.highrise.get_room_users()
            target_id = None
            for room_user, _ in room_users.content:
                if room_user.username.lower() == username.lower():
                    target_id = room_user.id
                    break

            if not target_id:
                await self.highrise.chat("User not found in room")
                return

            try:
                permissions = await self.highrise.get_room_privilege(target_id)
                setattr(permissions, role.lower(), False)
                await self.highrise.change_room_privilege(target_id, permissions)
                await self.highrise.chat(f"@{username} has been demoted from {role}")
            except Exception as e:
                await self.highrise.chat(f"Error: {e}")
                return

         if message.startswith("-roast"):
            parts = message.split()
            if len(parts) < 2 or not parts[1].startswith("@"):
                await self.highrise.chat("Usage: -roast @username")
                return
            target = parts[1][1:]  # Remove @ symbol
            roast = random.choice(roasts).format(target)
            await self.highrise.chat(roast)
            return

         if message.startswith("-fact"):
            parts = message.split()
            if len(parts) < 2 or not parts[1].startswith("@"):
                await self.highrise.chat("Usage: -fact @username")
                return
            target = parts[1][1:]  # Remove @ symbol
            fact = random.choice(facts).format(target)
            await self.highrise.chat(fact)
            return

         if message.startswith("-rizz"):
            parts = message.split()
            if len(parts) < 2 or not parts[1].startswith("@"):
                await self.highrise.chat("Usage: -rizz @username")
                return
            target = parts[1][1:]  # Remove @ symbol
            pickup = random.choice(pickup_lines).format(target)
            await self.highrise.chat(pickup)
            return
         if message.lower() == "-trivia":
             if self.current_trivia is None:
                 from trivia import trivia_questions
                 import random
                 self.current_trivia = random.choice(trivia_questions)
                 question = self.current_trivia["question"]
                 options = self.current_trivia["options"]
                 await self.highrise.chat(f"📝 TRIVIA TIME! \n\nQuestion: {question}\n\nOptions:\nA) {options['a']}\nB) {options['b']}\nC) {options['c']}\nD) {options['d']}\n\nType a, b, c, or d to answer!")
             else:
                 await self.highrise.chat("There's already an active trivia question!")
             return

         if message.lower() in ['a', 'b', 'c', 'd'] and self.current_trivia:
             if message.lower() == self.current_trivia["correct"]:
                 self.trivia_points[user.username] = self.trivia_points.get(user.username, 0) + 1
                 await self.highrise.chat(f"🎉 Correct! {user.username} got it right! They now have {self.trivia_points[user.username]} points!")
             else:
                 await self.highrise.chat(f"❌ Sorry {user.username}, that's incorrect! The correct answer was {self.current_trivia['correct'].upper()})")
             self.current_trivia = None
             return

         if message.lower() == "-points":
             if user.username in self.trivia_points:
                 await self.highrise.chat(f"🏆 {user.username} has {self.trivia_points[user.username]} trivia points!")
             else:
                 await self.highrise.chat(f"🏆 {user.username} has 0 trivia points!")
             return
         user_input = None
         if message.lower().startswith("-announce ") :
           try:
               privileges = await self.highrise.get_room_privilege(user.id)
               if privileges and privileges.moderator:
                 parts = message.split()
                 self.should_stop = None
                 if len(parts) >= 3:
                     user_input =  message[len("-announce "):]
                     await self.highrise.chat("Alright i will loop this message with intervals of 60 seconds.")
                     await self.announce(user_input,message)
           except Exception as e:
               print(f"Error checking privileges: {e}")
               await self.highrise.send_whisper(user.id, "Error checking permissions.")
         if message.lower().startswith("-clear") :
           try:
               privileges = await self.highrise.get_room_privilege(user.id)
               if privileges and privileges.moderator:
                   await self.highrise.chat (f"Announcement message cleared")
                   self.stop_announce()
                   return
           except Exception as e:
               print(f"Error checking privileges: {e}")
               await self.highrise.send_whisper(user.id, "Error checking permissions.")
         if message.lower().startswith("-turn on emote floor") :
           try:
               privileges = await self.highrise.get_room_privilege(user.id)
               if privileges and privileges.moderator:
                    if self.dance_floor_task is not None and not self.dance_floor_task.done():
                        await self.highrise.chat("Emote floor is already turned on.")
                    else:
                        self.dance_floor_task = asyncio.create_task(self.dance_floor())
                        await self.highrise.chat("Emote floor turned on.")
           except Exception as e:
               print(f"Error checking privileges: {e}")
               await self.highrise.send_whisper(user.id, "Error checking permissions.")
         if message.lower().startswith("-turn off emote floor") :
           try:
               privileges = await self.highrise.get_room_privilege(user.id)
               if privileges and privileges.moderator:
                    if self.dance_floor_task is None or self.dance_floor_task.done():
                        await self.highrise.chat("Emote floor is already turned off.")
                    else:
                        self.dance_floor_task.cancel()
                        await self.highrise.chat("Emote floor turned off.")
           except Exception as e:
               print(f"Error checking privileges: {e}")
               await self.highrise.send_whisper(user.id, "Error checking permissions.")
         if message.startswith(("-heart", "-love", "-wink", "-like")):
            try:
                parts = message.split()
                reaction_type = "heart"
                if message.startswith("-wink"):
                    reaction_type = "wink"
                elif message.startswith("-like"):
                    reaction_type = "thumbs"

                if len(parts) >= 2:
                    privileges = await self.highrise.get_room_privilege(user.id)

                    # Handle 'all' command (mods only)
                    if parts[1] == "all" and privileges and privileges.moderator:
                        count = 1
                        if len(parts) >= 3:
                            try:
                                count = min(int(parts[2]), 100)
                            except ValueError:
                                await self.highrise.chat(f"Invalid count. Usage: -{reaction_type} all [count]")
                                return

                        roomUsers = (await self.highrise.get_room_users()).content
                        for roomUser, _ in roomUsers:
                            if roomUser.id != Counter.bot_id:  # Skip bot user
                                for _ in range(count):
                                    await self.highrise.react(reaction_type, roomUser.id)
                                    await asyncio.sleep(0.1)
                        await self.highrise.chat(f"Sent {count} {reaction_type}(s) to everyone in the room")

                    # Handle @user command (available to all users)
                    elif parts[1].startswith("@"):
                        target_username = parts[1][1:]
                        count = 1
                        # Allow count parameter only for mods
                        if len(parts) >= 3 and privileges and privileges.moderator:
                            try:
                                count = min(int(parts[2]), 100)
                            except ValueError:
                                await self.highrise.chat(f"Invalid count. Usage: -{reaction_type} @username [count]")
                                return

                        room_users = await self.highrise.get_room_users()
                        target_id = None
                        for room_user, _ in room_users.content:
                            if room_user.username.lower() == target_username.lower():
                                target_id = room_user.id
                                break

                        if target_id:
                            for _ in range(count):
                                await self.highrise.react(reaction_type, target_id)
                                await asyncio.sleep(0.1)
                            await self.highrise.chat(f"Sent {count} {reaction_type}(s) to @{target_username}")
                        else:
                            await self.highrise.chat(f"User @{target_username} not found in room")
                    else:
                        await self.highrise.chat(f"Usage: -{reaction_type} @username" + (" [count]" if privileges and privileges.moderator else ""))
                else:
                    await self.highrise.chat(f"Usage: -{reaction_type} @username" + (" [count]" if privileges and privileges.moderator else ""))
            except Exception as e:
                print(f"Error: {e}")
                await self.highrise.send_whisper(user.id, "An error occurred while processing your command.")
         if message.startswith("-kick"):
           try:
               privileges = await self.highrise.get_room_privilege(user.id)
               if privileges and privileges.moderator:
                    parts = message.split()
                    if len(parts) < 2:
                        await self.highrise.chat(user.id, "Usage: -kick @username")
                        return

                    mention = parts[1]
                    username_to_kick = mention.lstrip('@')  # Remove the '@' symbol from the mention
                    response = await self.highrise.get_room_users()
                    users = [content[0] for content in response.content]  # Extract the User objects
                    user_ids = [user.id for user in users]  # Extract the user IDs

                    if username_to_kick.lower() in [user.username.lower() for user in users]:
                        user_index = [user.username.lower() for user in users].index(username_to_kick.lower())
                        user_id_to_kick = user_ids[user_index]
                        await self.highrise.moderate_room(user_id_to_kick, "kick")
                        await self.highrise.chat( f"Kicked {mention}.")
                    else:
                        await self.highrise.send_whisper(user.id, f"User {mention} is not in the room.")
               else:
                    await self.highrise.send_whisper(user.id, "You don't have moderator permissions.")
           except Exception as e:
               print(f"Error checking privileges: {e}")
               await self.highrise.send_whisper(user.id, "Error checking permissions.")

         elif message.startswith("-mute"):
           try:
               privileges = await self.highrise.get_room_privilege(user.id)
               if privileges and privileges.moderator:
                    parts = message.split()
                    if len(parts) < 2:
                        await self.highrise.chat(user.id, "Usage: -mute @username")
                        return

                    mention = parts[1]
                    username_to_mute = mention.lstrip('@')  # Remove the '@' symbol from the mention
                    response = await self.highrise.get_room_users()
                    users = [content[0] for content in response.content]  # Extract the User objects
                    user_ids = [user.id for user in users]  # Extract the user IDs

                    if username_to_mute.lower() in [user.username.lower() for user in users]:
                        user_index = [user.username.lower() for user in users].index(username_to_mute.lower())
                        user_id_to_mute = user_ids[user_index]
                        await self.highrise.moderate_room(user_id_to_mute, "mute",3600)  # Mute for 1 hour
                        await self.highrise.chat(f"Muted {mention} for 1 hour.")
                    else:
                        await self.highrise.send_whisper(user.id, f"User {mention} is not in the room.")
               else:
                    await self.highrise.send_whisper(user.id, "You don't have moderator permissions.")
           except Exception as e:
               print(f"Error checking privileges: {e}")
               await self.highrise.send_whisper(user.id, "Error checking permissions.")

         elif message.startswith("-unmute"):
           try:
               privileges = await self.highrise.get_room_privilege(user.id)
               if privileges and privileges.moderator:
                    parts = message.split()
                    if len(parts) < 2:
                        await self.highrise.chat(user.id, "Usage: -mute @username")
                        return

                    mention = parts[1]
                    username_to_mute = mention.lstrip('@')  # Remove the '@' symbol from the mention
                    response = await self.highrise.get_room_users()
                    users = [content[0] for content in response.content]  # Extract the User objects
                    user_ids = [user.id for user in users]  # Extract the user IDs

                    if username_to_mute.lower() in [user.username.lower() for user in users]:
                        user_index = [user.username.lower() for user in users].index(username_to_mute.lower())
                        user_id_to_mute = user_ids[user_index]
                        await self.highrise.moderate_room(user_id_to_mute, "mute",1)  # Mute for 1 hour
                        await self.highrise.chat(f"{mention} Unmuted.")
                    else:
                        await self.highrise.send_whisper(user.id, f"User {mention} is not in the room.")
               else:
                    await self.highrise.send_whisper(user.id, "You don't have moderator permissions.")
           except Exception as e:
               print(f"Error checking privileges: {e}")
               await self.highrise.send_whisper(user.id, "Error checking permissions.")

         elif message.startswith("-ban"):
           try:
               privileges = await self.highrise.get_room_privilege(user.id)
               if privileges and privileges.moderator:
                    parts = message.split()
                    if len(parts) < 2:
                        await self.highrise.chat(user.id, "Usage: -ban @username")
                        return

                    mention = parts[1]
                    username_to_ban = mention.lstrip('@')  # Remove the '@' symbol from the mention
                    response = await self.highrise.get_room_users()
                    users = [content[0] for content in response.content]  # Extract the User objects
                    user_ids = [user.id for user in users]  # Extract the user IDs

                    if username_to_ban.lower() in [user.username.lower() for user in users]:
                        user_index = [user.username.lower() for user in users].index(username_to_ban.lower())
                        user_id_to_ban = user_ids[user_index]
                        await self.highrise.moderate_room(user_id_to_ban, "ban", 3600)  # Ban for 1 hour
                        await self.highrise.chat(f"Banned {mention} for 1 hour.")
                    else:
                        await self.highrise.send_whisper(user.id, f"User {mention} is not in the room.")
               else:
                    await self.highrise.send_whisper(user.id, "You don't have moderator permissions.")
           except Exception as e:
               print(f"Error checking privileges: {e}")
               await self.highrise.send_whisper(user.id, "Error checking permissions.")






         if message.lower().lstrip().startswith("-list"):
            parts = message.split()
            try:
                    privileges = await self.highrise.get_room_privilege(user.id)
                    is_mod = privileges and privileges.moderator
                    is_vip = user.username.lower() in self.membership

                    if len(parts) == 1:
                        menu = "🎮 Main Menu:\n[1] General\n[2] Emotes\n[3] Teleport\n[5] Trivia"
                        if is_vip:
                            menu += "\n[6] VIP"
                        if is_mod:
                            menu += "\n[4] Moderator"
                        if user.username.lower() in self.owners:
                            menu += "\n[7] Owners"
                        menu += "\n\n❔ Type '-list number' to select"
                        await self.highrise.chat(menu)
                        return

                    choice = 0
                    try:
                        choice = int(parts[1])
                        if choice == 0:
                            menu = "🎮 Main Menu:\n[1] General\n[2] Emotes\n[3] Teleport\n[5] Trivia"
                            if is_vip:
                                menu += "\n[6] VIP"
                            if is_mod:
                                menu += "\n[4] Moderator"
                            if user.username.lower() in self.owners:
                                menu += "\n[7] Owners"
                            menu += "\n\n❔ Type '-list number' to select"
                            await self.highrise.chat(menu)
                            return
                    except ValueError:
                        pass

                    category = "invalid"
                    if choice != 0:
                        category_map = {
                            1: "general",
                            2: "emotes", 
                            3: "teleport",
                            4: "mod",
                            5: "trivia",
                            6: "vip",
                            7: "owners"
                        }
                        category = category_map.get(choice, "invalid")
                    else:
                        category = parts[1].lower()

                    if category == "general":
                        await self.highrise.chat("📋 General Commands:\n" + 
                            "• -list : Show command categories\n" +
                            "• -heart/wink/like @ <number> : Send reacts\n" +
                            "• -roast @user : Roast someone\n" +
                            "• -fact @user : Share a fact\n" +
                            "• -rizz @user : Use pickup lines")

                    elif category == "emotes":
                            await self.highrise.chat("🎭 Emote Commands Part 1 [1-15]:\n" +
                                "1:rest 2:enthused 3:yes 4:thewave 5:tired\n" +
                                "6:snowballfight 7:snowangel 8:shy 9:sad 10:no\n" +
                                "11:model 12:flirtywave 13:laugh 14:kiss 15:sweating")
                        
                            await self.highrise.chat("🎭 Part 2 [16-30]:\n" +
                                "16:hello 17:greedy 18:greedy 19:curtsy 20:confusion\n" +
                                "21:charging 22:bow 23:thumbsup 24:tummyache 25:flex\n" +
                                "26:cursing 27:raisetheroof 28:angry 29:savagedance 30:dontstartnow")
                        
                            await self.highrise.chat("🎭 Part 3 [31-45]:\n" +
                                "31:letsgoshopping 32:russiandance 33:pennysdance 34:macarena 35:kpopdance\n" +
                                "36:hyped 37:jinglebell 38:nervous 39:toilet 40:astronaut\n" +
                                "41:astronaut 42:astronaut 43:swordfight 44:timejump 45:snake")
                        
                            await self.highrise.chat("🎭 Part 4 [46-60]:\n" +
                                "46:snake 47:float 48:telekinesis 49:penguindance 50:creepypuppet\n" +
                                "51:sleigh 52:maniac 53:energyball 54:astronaut 55:frog\n" +
                                "56:superpose 57:cute 58:tiktokdance9 59:weirddance 60:tiktokdance10")
                        
                            await self.highrise.chat("🎭 Part 5 [61-75]:\n" +
                                "61:pose7 62:pose8 63:casualdance 64:pose1 65:pose3\n" +
                                "66:pose5 67:cutey 68:punkguitar 69:fashionista 70:gravity\n" +
                                "71:icecreamdance 72:wrongdance 73:uwu 74:tiktokdance4 75:advancedshy")
                        
                            await self.highrise.chat("🎭 Part 6 [76-90]:\n" +
                                "76:animedance 77:kawaii 78:scritchy 79:iceskating 80:surprisebig\n" +
                                "81:celebrationstep 82:creepycute 83:pose10 84:boxer 85:headblowup\n" +
                                "86:ditzypose 87:teleporting 88:touch 89:airguitar 90:thisisforyou")
                        
                            await self.highrise.chat("🎭 Part 7 [91-105]:\n" +
                                "91:pushit 92:rest 93:zombie 94:relaxed 95:attentive\n" +
                                "96:sleepy 97:poutyface 98:posh 99:sleepy 100:taploop\n" +
                                "101:shy 102:bummed 103:chillin 104:annoyed 105:aerobics")
                        
                            await self.highrise.chat("🎭 Part 8 [106-120]:\n" +
                                "106:ponder 107:heropose 108:relaxing 109:cozynap 110:boogieswing\n" +
                                "111:feelthebeat 112:irritated 113:ibelieveicanfly 114:think 115:theatrical\n" +
                                "116:tapdance 117:superrun 118:superpunch 119:sumofight 120:thumbsuck")
                        
                            await self.highrise.chat("🎭 Part 9 [121-134]:\n" +
                                "121:splitsdrop 122:secrethandshake 123:ropepull 124:roll 125:rofl\n" +
                                "126:robot 127:rainbow 128:proposing 129:peekaboo 130:peace\n" +
                                "131:panic 132:ninjarun 133:nightfever 134:monsterfail\n" +
                                "Use: number or -loop [number] • -stop loop")

                    elif category == "teleport":
                        await self.highrise.chat("🚀 Teleport Commands:\n" +
                            "• -f1/-floor1 : Ground floor\n" +
                            "• -f2/-floor2 : Second floor\n" +
                            "• -f3/-floor3 : Third floor\n" +
                            "• -vip/-v : VIP area (VIP only)\n" +
                            "• -pos : Check your position")

                    elif category == "mod":
                        if not is_mod:
                            await self.highrise.chat("❌ You need moderator permissions to view these commands.")
                            return
                        await self.highrise.chat("⚡ Moderator Commands (Part 1):\n" +
                            "• -kick @user : Kick user\n" +
                            "• -ban @user : Ban user\n" +
                            "• -mute/unmute @user : Mute controls\n" +
                            "• -give/remove @user vip : Permissions\n"+
                            "• -here @user/-to @user : Teleport controls\n" +
                            "• -tele @user x y z : Custom teleport \n")
                        await asyncio.sleep(0.5)
                        await self.highrise.chat("⚡ Moderator Commands (Part 2):\n" +
                            "• -announce [text] : Start announcement\n" +
                            "• -clear : Stop announcement\n" +
                            "• -heart/wink/like all : Group reactions\n" +
                            "• -turn on/off emote floor : Dance floor\n")

                    elif category == "trivia":
                        await self.highrise.chat("🎯 Trivia Commands:\n" +
                            "• -trivia : Start a new trivia question\n" +
                            "• -points : Check your trivia points\n" +
                            "• Answer with a/b/c/d")

                    elif category == "vip":
                        if not is_vip and not is_mod:
                            await self.highrise.chat("❌ You need VIP permissions to view these commands.")
                            return
                        await self.highrise.chat("👑 VIP Commands:\n" +
                            "• -vip/-v : Teleport to VIP area\n" +
                            "• Special room access and features")
                    elif category == "owners":
                        if user.username.lower() not in self.owners:
                            await self.highrise.chat("❌ You need owner permissions to view these commands.")
                            return
                        await self.highrise.chat("👑 Owner Commands:\n" +
                            "• -promote/@user mod/designer : Promote users to roles\n" +
                            "• -demote/@user mod/designer : Demote users from roles\n" +
                            "• -tip @user amount : Tip a user\n" +
                            "• -tipall amount : Tip all users\n" +
                            "• Full control over room settings and moderation")

                    else:
                        await self.highrise.chat("❌ Invalid category. Use -list to see available categories.")



            except Exception as e:
               print(f"Error checking privileges: {e}")
               await self.highrise.send_whisper(user.id, "Error checking permissions.")


         if message.lstrip().startswith(("-give","-remove","-here","-to")):
            response = await self.highrise.get_room_users()
            users = [content[0] for content in response.content]
            usernames = [user.username.lower() for user in users]
            parts = message[1:].split()
            args = parts[1:]

            if len(args) < 1:
                await self.highrise.send_whisper(user.id, f"Usage !{parts[0]} <@Alionardo_>")
                return
            elif args[0][0] != "@":
                await self.highrise.send_whisper(user.id, "Invalid user format. Please use '@username'.")
                return
            elif args[0][1:].lower() not in usernames:
                await self.highrise.send_whisper(user.id, f"{args[0][1:]} is not in the room.")
                return
            user_upg = next((u.username for u in users if u.username.lower() == args[0][1:].lower()), None)
            user_id = next((u.id for u in users if u.username.lower() == args[0][1:].lower()), None)
            username = next((u.username.lower() for u in users if u.username.lower() == args[0][1:].lower()), None)
            if not user_id:
                await self.highrise.send_whisper(user.id, f"User {args[0][1:]} not found")
                return                     
            try:


                if message.lower().startswith("-give") and message.lower().endswith("vip"):   
                  try:
                      privileges = await self.highrise.get_room_privilege(user.id)
                      if privileges and privileges.moderator:
                         await self.highrise.chat(f"{user_upg} is promoted to VIP by {user.username}")
                         if user_upg.lower() not in self.membership:
                               self.membership.append(user_upg.lower())
                               self.save_membership()
                      else:
                         await self.highrise.send_whisper(user.id, "You don't have moderator permissions.")
                  except Exception as e:
                      print(f"Error checking privileges: {e}")
                      await self.highrise.send_whisper(user.id, "Error checking permissions.")

                elif message.lower().startswith("-remove") and message.lower().endswith("vip"):
                  try:
                      privileges = await self.highrise.get_room_privilege(user.id)
                      if privileges and privileges.moderator:
                        if user_upg.lower() in self.membership:
                           self.membership.remove(user_upg.lower())
                           self.save_membership()
                           await self.highrise.chat(f"{user_upg} is no longer a VIP.")
                        else:
                            await self.highrise.send_whisper(user.id, "You don't have moderator permissions.")
                      else:
                         await self.highrise.send_whisper(user.id, "You don't have moderator permissions.")
                  except Exception as e:
                      print(f"Error checking privileges: {e}")
                      await self.highrise.send_whisper(user.id, "Error checking permissions.")
                elif message.lower().startswith("-here"):
                   try:
                       privileges = await self.highrise.get_room_privilege(user.id)
                       if privileges and privileges.moderator:
                          target_username = user_upg
                          if target_username not in owners :
                              await self.teleport_user_next_to(target_username, user)
                       else:
                          await self.highrise.send_whisper(user.id, "You don't have moderator permissions.")
                   except Exception as e:
                       print(f"Error checking privileges: {e}")
                       await self.highrise.send_whisper(user.id, "Error checking permissions.")
                elif message.lower().startswith("-to"):
                  try:
                      privileges = await self.highrise.get_room_privilege(user.id)
                      if privileges and privileges.moderator:
                            target_username = user_upg
                            await self.teleport_to(user, target_username)
                      else:
                         await self.highrise.send_whisper(user.id, "You don't have moderator permissions.")
                  except Exception as e:
                      print(f"Error checking privileges: {e}")
                      await self.highrise.send_whisper(user.id, "Error checking permissions.")
            except Exception as e:
             print(f"An exception occurred[Due To {parts[0][1:]}]: {e}")

         # Floor teleport commands
         floor_positions = {
             'f1': (14, 0, 9.5, "Floor 1"),
             'f2': (14, 6.5, 12, "Floor 2"),
             'f3': (14, 13, 13, "Floor 3")
         }

         if message.lower().startswith('-pos'):
             response = await self.highrise.get_room_users()
             for room_user, pos in response.content:
                 if room_user.id == user.id:
                     if isinstance(pos, Position):
                         await self.highrise.send_whisper(user.id, f"📍 Your position: x={pos.x}, y={pos.y}, z={pos.z}")
                     break
             return

         if message.lower().startswith('-tele'):
             parts = message.split()
             if len(parts) >= 3:  # -tele @username destination
                 if not parts[1].startswith('@'):
                     await self.highrise.send_whisper(user.id, "❌ Usage: -tele @username [f1/f2/f3 or x y z]")
                     return

                 target_username = parts[1][1:]
                 destination = parts[2].lower()

                 if destination in floor_positions:
                     x, y, z, floor_name = floor_positions[destination]
                     await self.teleport_user_to(target_username, Position(x, y, z), floor_name)
                 elif len(parts) >= 5:  # Custom coordinates
                     try:
                         x, y, z = float(parts[2]), float(parts[3]), float(parts[4])
                         await self.teleport_user_to(target_username, Position(x, y, z), f"position ({x}, {y}, z)")
                     except ValueError:
                         await self.highrise.send_whisper(user.id, "❌ Invalid coordinates format")
                 else:
                     await self.highrise.send_whisper(user.id, "❌ Usage: -tele @username [f1/f2/f3 or x y z]")
             else:
                 await self.highrise.send_whisper(user.id, "❌ Usage: -tele @username [f1/f2/f3 or x y z]")

         # Regular floor commands for self-teleport
         for cmd, pos in floor_positions.items():
             if message.lower() in [f'-{cmd}', cmd]:
                 await self.highrise.teleport(user.id, Position(pos[0], pos[1], pos[2]))
                 await self.highrise.send_whisper(user.id, f"📍 Teleported to {pos[3]}")
                 break

         # Custom teleport command
         if message.lower().startswith("-tele"):
           try:
               privileges = await self.highrise.get_room_privilege(user.id)
               if privileges and privileges.moderator:
                    parts = message.split()
                    if len(parts) >= 5 and parts[1].startswith("@"):
                        try:
                            target_username = parts[1][1:]
                            x = float(parts[2])
                            y = float(parts[3])
                            z = float(parts[4])
                            await self.teleport_user_to(target_username, Position(x, y, z), f"position ({x}, {y}, {z})")
                        except ValueError:
                            await self.highrise.send_whisper(user.id, "❌ Invalid coordinates! Format: -tele @username x y z")
                    else:
                        await self.highrise.send_whisper(user.id, "❌ Usage: -tele @username x y z")
               else:
                    await self.highrise.send_whisper(user.id, "You don't have moderator permissions.")
           except Exception as e:
               print(f"Error checking privileges: {e}")
               await self.highrise.send_whisper(user.id, "Error checking permissions.")
         if message.lower().startswith(('-v','-vip')):
             if user.username.lower() in self.membership or user.username.lower() in self.moderators:
                await self.highrise.teleport(f"{user.id}", Position(15.5,17.5,12))
             else:
              await self.highrise.send_whisper(user.id,"Only VIP are able use this teleport ,you can ask for mod to assist you get ur vip.")  
         if message.lower().startswith(('-mod')):
           try:
               privileges = await self.highrise.get_room_privilege(user.id)
               if privileges and privileges.moderator:
                    await self.highrise.teleport(f"{user.id}", Position(19.5,17.25,2.5))
               else:
                    await self.highrise.send_whisper(user.id,"Only mods/Admins can use this teleport.")
           except Exception as e:
               print(f"Error checking privileges: {e}")
               await self.highrise.send_whisper(user.id, "Error checking permissions.")
         if message.lower().startswith("-loop"):
           parts = message.split()
           E = parts[1]
           E = int(E)
           emote_text, emote_time = await self.get_emote_E(E)
           emote_time -= 1
           user_id = user.id  
           if user.id in self.continuous_emote_tasks and not self.continuous_emote_tasks[user.id].cancelled():
              await self.stop_continuous_emote(user.id)
              task = asyncio.create_task(self.send_continuous_emote(emote_text,user_id,emote_time))
              self.continuous_emote_tasks[user.id] = task
           else:
              task = asyncio.create_task(self.send_continuous_emote(emote_text,user_id,emote_time))
              self.continuous_emote_tasks[user.id] = task  

         elif message.lower().startswith("-stop loop"):
            if user.id in self.continuous_emote_tasks and not self.continuous_emote_tasks[user.id].cancelled():
                await self.stop_continuous_emote(user.id)
                await self.highrise.chat("Continuous emote has been stopped.")
            else:
                await self.highrise.chat("You don't have an active loop_emote.")
         if  message.isdigit() and 1 <= int(message) <= 134:
              parts = message.split()
              E = parts[0]
              E = int(E)
              emote_text, emote_time = await self.get_emote_E(E)
              tasks = [asyncio.create_task(self.highrise.send_emote(emote_text, user.id))]
              await asyncio.wait(tasks)
         if message == "-fit":
          shirt = ["shirt-n_room12019buttondownblack"]
          pant = ["pants-n_room12019blackacidwashjeans"]
          item_top = random.choice(shirt)
          item_bottom = random.choice(pant)
          xox = await self.highrise.set_outfit(outfit=[
         Item(type='clothing', 
          amount=1, 
          id='body-flesh',
          account_bound=False,
          active_palette=23),
         Item(type='clothing',
          amount=1,
          id='shirt-n_starteritems2019maletshirtwhite',
         account_bound=False,
          active_palette=-1),
         Item(type='clothing', 
        amount=1, 
        id='pants-n_room32019baggytrackpantsred',
        account_bound=False,
        active_palette=-1),
        Item(type='clothing', 
        amount=1, 
        id='nose-n_01',
        account_bound=False,
        active_palette=-1),
        Item(type='clothing',
        amount=1, 
        id='necklace-n_room12019chain', 
        account_bound=False,
        active_palette=-1),
        Item(type='clothing', 
        amount=1, 
        id='watch-n_room12019watch', 
        account_bound=False,
        active_palette=-1),
        Item(type='clothing', 
        amount=1, id='shoes-n_room22019tallsocks', 
        account_bound=False,
        active_palette=-1), 

        Item(type='clothing',
        amount=1, 
        id='freckle-n_basic2018freckle22', 
        account_bound=False,
        active_palette=-1),
        Item(type='clothing',
        amount=1,
        id='mouth-basic2018yummouth',
        account_bound=False,
        active_palette=0),
        Item(type='clothing', amount=1, id='glasses-n_10', active_palette=1),
        Item(type='clothing', amount=1, id='hair_front-m_19', account_bound=False, active_palette=6),
        Item(type='clothing', amount=1, id='hair_back-m_19', account_bound=False, active_palette=6),
        Item(type='clothing', 
        amount=1, 
        id='eye-n_basic2018nudesquare',
        account_bound=False,
        active_palette=8),
        Item(type='clothing', 
        amount=1,
        id='eyebrow-n_basic2018newbrows16', 
        account_bound=False,
        active_palette=6)

        ]) 


         if  message.lower().startswith("-wallet"):
           try:
               privileges = await self.highrise.get_room_privilege(user.id)
               if privileges and privileges.moderator:

                  wallet = (await self.highrise.get_wallet()).content
                  await self.highrise.send_whisper(user.id, f"The bot wallet contains {wallet[0].amount} {wallet[0].type}")

               else: 
                await  self.highrise.send_whisper(user.id, "Only Moderators Can View the Wallet")
           except Exception as e:
               print(f"Error checking privileges: {e}")
               await self.highrise.send_whisper(user.id, "Error checking permissions.")

         if message.lower().startswith("-tip ") and user.username.lower() in self.owners:
            parts = message.split()
            if len(parts) != 3 or not parts[1].startswith("@"):
                await self.highrise.chat("Usage: -tip @username amount")
                return

            try:
                amount = int(parts[2])
                if amount <= 0:
                    await self.highrise.chat("Amount must be positive")
                    return
            except ValueError:
                await self.highrise.chat("Invalid amount")
                return

            target_username = parts[1][1:]
            room_users = await self.highrise.get_room_users()
            target_id = None

            for room_user, _ in room_users.content:
                if room_user.username.lower() == target_username.lower():
                    target_id = room_user.id
                    break

            if not target_id:
                await self.highrise.chat(f"User {target_username} not found in room")
                return

            wallet = await self.check_wallet()
            if wallet >= amount:
                if await self.tip_amount(target_id, amount):
                    await self.highrise.chat(f"Successfully tipped {amount} gold to @{target_username}")
                else:
                    await self.highrise.chat("Failed to send tip")
            else:
                await self.highrise.chat(f"Insufficient funds. Bot has {wallet} gold.")

         elif message.lower().startswith("-tipall ") and user.username.lower() in self.owners:
            parts = message.split()
            if len(parts) != 2:
                await self.highrise.chat("Usage: -tipall amount")
                return

            try:
                amount = int(parts[1])
                if amount <= 0:
                    await self.highrise.chat("Amount must be positive")
                    return
            except ValueError:
                await self.highrise.chat("Invalid amount")
                return

            room_users = await self.highrise.get_room_users()
            wallet = await self.check_wallet()
            room_users_count = sum(1 for room_user, _ in room_users.content if room_user.id != Counter.bot_id)
            total_needed = amount * room_users_count
            
            if wallet >= total_needed:
                success_count = 0
                for room_user, _ in room_users.content:
                    if room_user.id != Counter.bot_id:  # Don't tip the bot
                        if await self.tip_amount(room_user.id, amount):
                            success_count += 1
                await self.highrise.chat(f"Successfully tipped {amount} gold to {success_count} users")
            else:
                await self.highrise.chat(f"Insufficient funds. Need {total_needed} gold but bot only has {wallet} gold.")

       

      except Exception as e:
        print(f"An exception occured: {e}")  

    async def send_continuous_emote(self, emote_text ,user_id,emote_time):
      try:
          while True:                    
                tasks = [asyncio.create_task(self.highrise.send_emote(emote_text, user_id))]
                await asyncio.wait(tasks)
                await asyncio.sleep(emote_time)
                await asyncio.sleep(1)
      except Exception as e:
                print(f"{e}")


    async def stop_continuous_emote(self, user_id: int):
      if user_id in self.continuous_emote_tasks and not self.continuous_emote_tasks[user_id].cancelled():
          task = self.continuous_emote_tasks[user_id]
          task.cancel()
          with contextlib.suppress(asyncio.CancelledError):
              await task
          del self.continuous_emote_tasks[user_id]

    async def follow_user(self, target_username: str):
      while self.following_username == target_username:

          response = await self.highrise.get_room_users()
          target_user_position = None
          for user_info in response.content:
              if user_info[0].username.lower() == target_username.lower():
                  target_user_position = user_info[1]
                  break

          if target_user_position:
              nearby_position = Position(target_user_position.x + 1.0, target_user_position.y, target_user_position.z)
              await self.highrise.walk_to(nearby_position)

              await asyncio.sleep(2)
    async def get_emote_E(self, target) -> None: 

     try:
        emote_info = self.Emotes.get(target)
        return emote_info
     except ValueError:
        pass
    async def on_whisper(self, user: User, message: str ) -> None:

        if message == "here":
           try:
               privileges = await self.highrise.get_room_privilege(user.id)
               if privileges and privileges.moderator:
                    response = await self.highrise.get_room_users()
                    users = [content for content in response.content]
                    for u in users:
                        if u[0].id == user.id:
                            try:
                                await self.highrise.teleport(Counter.bot_id,Position((u[1].x),(u[1].y),(u[1].z),"FrontRight"))


                                break
                            except:

                                pass
               else:
                    await self.highrise.send_whisper(user.id, "You don't have moderator permissions.")
           except Exception as e:
               print(f"Error checking privileges: {e}")
               await self.highrise.send_whisper(user.id, "Error checking permissions.")

        if message.startswith("-say"):
           try:
               privileges = await self.highrise.get_room_privilege(user.id)
               if privileges and privileges.moderator:
                    text = message.replace("-say", "").strip()
                    await self.highrise.chat(text)
               else:
                    await self.highrise.send_whisper(user.id, "You don't have moderator permissions.")
           except Exception as e:
               print(f"Error checking privileges: {e}")
               await self.highrise.send_whisper(user.id, "Error checking permissions.")




        elif message.startswith("-come"):
           try:
               privileges = await self.highrise.get_room_privilege(user.id)
               if privileges and privileges.moderator:
                    response = await self.highrise.get_room_users()
                    your_pos = None
                    for content in response.content:
                        if content[0].id == user.id:
                            if isinstance(content[1], Position):
                                your_pos = content[1]
                                break
                    if not your_pos:
                        await self.highrise.send_whisper(user.id, "Invalid coordinates!")
                        return
                    await self.highrise.chat(f"@{user.username} I'm coming ..")
                    await self.highrise.walk_to(your_pos)
               else:
                    await self.highrise.send_whisper(user.id, "You don't have moderator permissions.")
           except Exception as e:
               print(f"Error checking privileges: {e}")
               await self.highrise.send_whisper(user.id, "Error checking permissions.")

        elif message.lower().startswith("-follow"):

            target_username = message.split("@")[1].strip()

            if target_username.lower() == self.following_username:
                await self.highrise.send_whisper(user.id,"I am already following.")
            elif message.startswith("-say"):
              try:
                  privileges = await self.highrise.get_room_privilege(user.id)
                  if privileges and privileges.moderator:
                       text = message.replace("-say", "").strip()
                       await self.highrise.chat(text)
                  else:
                       await self.highrise.send_whisper(user.id, "You don't have moderator permissions.")
              except Exception as e:
                  print(f"Error checking privileges: {e}")
                  await self.highrise.send_whisper(user.id, "Error checking permissions.")
            else:
                self.following_username = target_username
                await self.highrise.chat(f"hey {target_username}.")

                await self.follow_user(target_username)
        elif message.lower() == "-stop following":
            self.following_username = None

            await self.highrise.walk_to(Position(18.5,6.25,2, facing='FrontRight'))





    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        try:
            print(f"{sender.username} tipped {receiver.username} an amount of {tip.amount}")

        except Exception as e:
            print(f"Error: {e}")

    async def on_user_move(self, user: User, pos: Position | AnchorPosition) -> None:
      if user.username == " Alionardo_":
         print(f"{user.username}: {pos}")
      if user:

        if self.dance_floor_pos:

            if isinstance(pos, Position):

                for dance_floor_info in self.dance_floor_pos:

                    if (
                        dance_floor_info[0] <= pos.x <= dance_floor_info[1] and
                        dance_floor_info[2] <= pos.y <= dance_floor_info[3] and
                        dance_floor_info[4] <= pos.z <= dance_floor_info[5]
                    ):

                        if user.id not in self.dancer:
                            self.dancer.append(user.id)

                        return

            # If not in any dance floor area
            if user.id in self.dancer:
                self.dancer.remove(user.id)



        print(f"{user.username}: {pos}")
    def save_moderators(self):
        with open("moderators.json", "w") as f:
            json.dump(self.moderators, f)

    def load_moderators(self):
        try:
            with open("moderators.json", "r") as f:
                self.moderators = json.load(f)
        except FileNotFoundError:
            self.moderators = []

    async def mods(self, user: User, message:str):
        pass
    async def check_wallet(self):
        wallet = (await self.highrise.get_wallet()).content
        return wallet[0].amount

    async def tip_amount(self, target_id, amount):
        try:
            bars_dictionary = {10000: "gold_bar_10k",
                             5000: "gold_bar_5000",
                             1000: "gold_bar_1k",
                             500: "gold_bar_500",
                             100: "gold_bar_100",
                             50: "gold_bar_50",
                             10: "gold_bar_10",
                             5: "gold_bar_5",
                             1: "gold_bar_1"}
            fees_dictionary = {10000: 1000,
                             5000: 500,
                             1000: 100,
                             500: 50,
                             100: 10,
                             50: 5,
                             10: 1,
                             5: 1,
                             1: 1}
            tip = []
            total = 0
            temp_amount = amount
            for bar in sorted(bars_dictionary.keys(), reverse=True):
                if temp_amount >= bar:
                    bar_amount = temp_amount // bar
                    temp_amount = temp_amount % bar
                    for i in range(bar_amount):
                        tip.append(bars_dictionary[bar])
                        total += bar + fees_dictionary[bar]

            bot_wallet = await self.highrise.get_wallet()
            bot_amount = bot_wallet.content[0].amount
            
            if total > bot_amount:
                return False
                
            tip_string = ",".join(tip)
            await self.highrise.tip_user(target_id, tip_string)
            return True
        except Exception as e:
            print(f"Error sending tip: {e}")
            return False
