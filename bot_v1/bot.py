from javascript import require, On, Once, AsyncTask, once, off

# Import the javascript libraries
mineflayer = require("mineflayer")
pathfinder = require('mineflayer-pathfinder')
mcData = require('minecraft-data')

RANGE_GOAL = 1
# Global bot parameters
server_host = "mc.imperiacraft.ru"
server_port = 25565
reconnect = True
bots = 1


class MCBot:

    def __init__(self, bot_name):
        self.bot_args = {
            "host": server_host,
            "port": server_port,
            "username": bot_name,
            "hideErrors": False,
        }
        self.reconnect = reconnect
        self.bot_name = bot_name
        self.start_bot()

    # Start mineflayer bot
    def start_bot(self):
        self.bot = mineflayer.createBot(self.bot_args)
        self.bot.loadPlugin(pathfinder.pathfinder)
        self.start_events()

    # Attach mineflayer events to bot
    def start_events(self):
        @On(self.bot, 'spawn')
        def handle(*args):
            print("I spawned 👋")
            self.mcData = mcData(self.bot.version)
            self.movements = pathfinder.Movements(self.bot, self.mcData)

        # Login event: Triggers on bot login
        @On(self.bot, "login")
        def login(this):
            self.bot.chat("/login 777Haker777")
            self.bot.chat("всем ку")
            self.bot_socket = self.bot._client.socket
            print(
                f"[{self.bot_name}] Logged in to {self.bot_socket.server if self.bot_socket.server else self.bot_socket._host }"
            )

        # Kicked event: Triggers on kick from server
        @On(self.bot, "kicked")
        def kicked(this, reason, loggedIn):
            if loggedIn:
                print(f"[{self.bot_name}] Kicked whilst trying to connect: {reason}")

        # Chat event: Triggers on chat message
        @On(self.bot, "messagestr")
        def messagestr(this, message, messagePosition, jsonMsg, sender, verified=None):
            if messagePosition == "chat" and "quit" in message:
                self.reconnect = False
                this.quit()

        # End event: Triggers on disconnect from server
        @On(self.bot, "end")
        def end(this, reason):
            print(f"[{self.bot_name}] Disconnected: {reason}")

            # Turn off old events
            off(self.bot, "login", login)
            off(self.bot, "kicked", kicked)
            off(self.bot, "messagestr", messagestr)

            # Reconnect
            if self.reconnect:
                print(f"[{self.bot_name}] Attempting to reconnect")
                self.start_bot()

            # Last event listener
            off(self.bot, "end", end)

        def msghandler(this, user, message, *args):
            if self.bot_name in message:
                ai = ASK_AI()
                response = ai.prompt_send(message)  # Call the method
                self.bot.chat(response)
            else:
                if "как вы" in message:
                    self.bot.chat(f"Эй ты {user}, у меня {self.bot.health} хп;)")
                if "сюда" in message:
                    player = self.bot.players[user]
                    print("Target", player)
                    self.bot.chat("Я уже иду к тебе!")
                    target = player.entity
                    if not target:
                        self.bot.chat("стой! Я тебя не вижу!")
                        self.bot.chat(f"/tpa {user}")
                        return

                    pos = target.position
                    self.bot.pathfinder.setMovements(self.movements)
                    self.bot.pathfinder.setGoal(pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, RANGE_GOAL))
                if "где" in message:
                    self.bot.chat(f"я на {self.bot.entity.position}")
                if "атакуй" in message:
                    target_name = message.split("атакуй ")[1]
                    self.attack_mobs(target_name)
                if "добывай" in message:
                    block_name = message.split("добывай ")[1]
                    self.mine_block(block_name)
                if "отдай мне" in message:
                    self.give_items(user)
                if "тп" in message:
                    self.bot.chat("/tpaccept")
                if "домой" in message:
                    self.bot.chat("я возвращаюсь домой")
                    self.bot.chat("/home")
                if "дом здесь" in message:
                    self.bot.chat("я установил точку дома")
                    self.bot.chat("/sethome")

    def attack_mobs(self, target_name):
        target_entity = self.mcData.entitiesByName[target_name]
        if not target_entity:
            self.bot.chat("Я не знаю такого моба!")
            return

        @On(self.bot, "physicsTick")
        def attack_loop(this):
            target = self.bot.nearestEntity(lambda entity: entity.name == target_name and entity.type == 'mob')
            if target:
                if self.bot.entity.position.distanceTo(target.position) < RANGE_GOAL:
                    self.bot.attack(target)
                else:
                    self.bot.pathfinder.setGoal(pathfinder.goals.GoalNear(target.position.x, target.position.y, target.position.z, RANGE_GOAL))
            else:
                off(self.bot, "physicsTick", attack_loop)

    def mine_block(self, block_name):
        block_type = self.mcData.blocksByName[block_name]
        if not block_type:
            self.bot.chat("Я не знаю такого блока!")
            return

        @On(self.bot, "physicsTick")
        def mine_loop(this):
            target_block = self.bot.findBlock({
                'matching': block_type.id,
                'maxDistance': 32
            })

            if target_block:
                if self.bot.entity.position.distanceTo(target_block.position) < RANGE_GOAL:
                    self.bot.dig(target_block)
                else:
                    self.bot.pathfinder.setGoal(pathfinder.goals.GoalNear(target_block.position.x, target_block.position.y, target_block.position.z, RANGE_GOAL))
            else:
                off(self.bot, "physicsTick", mine_loop)

    def give_items(self, user):
        player = self.bot.players[user]
        target = player.entity

        if not target:
            self.bot.chat("Я тебя не вижу!")
            return

        pos = target.position
        self.bot.pathfinder.setMovements(self.movements)
        self.bot.pathfinder.setGoal(pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, RANGE_GOAL))

        @Once(self.bot, "goal_reached")
        def drop_items(this):
            for item in self.bot.inventory.items():
                self.bot.tossStack(item)


bot = MCBot(f"xxx")
