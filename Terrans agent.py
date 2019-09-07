from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
from absl import app
import random

# Resources for this code
# https://itnext.io/build-a-zerg-bot-with-pysc2-2-0-295375d2f58e
# https://github.com/deepmind/pysc2/blob/master/docs/environment.md
# https://github.com/deepmind/pysc2/blob/master/pysc2/lib/actions.py

class TerranAgent(base_agent.BaseAgent):

  def __init__(self):
    super(TerranAgent, self).__init__()
    self.attack_coordinates = None
    self.abajo = False

  # This function verifies that the action that you want to perform is available
  def can_do(self, obs, action):
    return action in obs.observation.available_actions

  # This function verifies if a unit or several units are selected
  def unit_type_is_selected(self, obs, unit_type):
    if (len(obs.observation.single_select) > 0 and
        obs.observation.single_select[0].unit_type == unit_type):
      return True

    if (len(obs.observation.multi_select) > 0 and
        obs.observation.multi_select[0].unit_type == unit_type):
      return True

    return False
  # This function gets the array of units of any unit_type that you indicate
  def get_units_by_type(self, obs, unit_type):
    return [unit for unit in obs.observation.feature_units
            if unit.unit_type == unit_type]

  # In this function is where all of the actions get done
  def step(self, obs):
    super(TerranAgent, self).step(obs)

    # The agent observe its position to know where to assign the
    # attack_coordinates and is also usefull for the position of the barracks
    # and the supply_depots
    if obs.first():
      player_y, player_x = (obs.observation.feature_minimap.player_relative ==
                            features.PlayerRelative.SELF).nonzero()
      xmean = player_x.mean()
      ymean = player_y.mean()

      if xmean <= 31 and ymean <= 31:
        self.abajo = False
        self.attack_coordinates = (49, 49)
      else:
        self.abajo = True
        self.attack_coordinates = (12, 16)

    # "obs.observation.player.minerals" get the amount of minerals that you have
    # at the moment
    minerals = obs.observation.player.minerals
    # Gets the array of supply depots on screen
    supply_depots = self.get_units_by_type(obs, units.Terran.SupplyDepot)
    # Build the first supply_depot
    if len(supply_depots) < 1 and minerals >= 100:
      # Verifies that a SCV is selected
      if self.unit_type_is_selected(obs, units.Terran.SCV):
        # Verifies that the action is available on screen
        if self.can_do(obs,actions.FUNCTIONS.Build_SupplyDepot_screen.id):
          # Action of building supply depot
          return actions.FUNCTIONS.Build_SupplyDepot_screen("now", (30, 5))

      # Gets the array of SCVs on screen
      scvs = self.get_units_by_type(obs,units.Terran.SCV)
      if len(scvs) > 0:
        # Chose a random SCV
        scvs = random.choice(scvs)
        # Action of selecting SCV
        return actions.FUNCTIONS.select_point("select_all_type", (scvs.x, scvs.y))

    # Gets the array of marines on screen
    marines = self.get_units_by_type(obs, units.Terran.Marine)
    # Attack the enemy
    if len(marines) >= 25:
      # Verifies that marines are selected
      if self.unit_type_is_selected(obs, units.Terran.Marine):
        # Verifies that the action is available on screen
        if self.can_do(obs, actions.FUNCTIONS.Attack_minimap.id):
          # Action of attacking
          return actions.FUNCTIONS.Attack_minimap("now",
                                                  self.attack_coordinates)

      # Select marines
      if self.can_do(obs, actions.FUNCTIONS.select_army.id):
        # Action of marines selection
        return actions.FUNCTIONS.select_army("select")

    # Gets the array of barracks on screen
    barracks = self.get_units_by_type(obs, units.Terran.Barracks)
    # Start training marines
    if len (barracks) > 3 and len(supply_depots) > 4 and minerals > 50:
      # Verifies that a barrack is selected
      if self.unit_type_is_selected(obs, units.Terran.Barracks):
        # Verifies that the action is available on screen
        if self.can_do(obs, actions.FUNCTIONS.Train_Marine_quick.id):
          # Action of marine training
          return actions.FUNCTIONS.Train_Marine_quick("now")

      # Chose a barrack
      barracks = random.choice(barracks)
      # Action of selecting barracks
      return actions.FUNCTIONS.select_point("select_all_type", (
                                                barracks.x,
                                                barracks.y))

    # Build barracks
    if len(barracks) < 4:
      # Verifies that there are enough minerals to build barracks
      if minerals > 150:
        # Verifies that an SCV is selected
        if self.unit_type_is_selected(obs, units.Terran.SCV):
          # Verifies that the action is available on screen
          if self.can_do(obs,actions.FUNCTIONS.Build_Barracks_screen.id):
            # Here we use the flag "abajo" in order to see our position and
            # get the cordinates for our barracks
            if self.abajo:
              # Actions of Building barracks in specific coordinate depending on
              # which number of barrack it is
              if len(barracks)==0:
                return actions.FUNCTIONS.Build_Barracks_screen("now", (7, 10))
              elif len(barracks)==1:
                return actions.FUNCTIONS.Build_Barracks_screen("now", (7, 20))
              elif len(barracks)==2:
                return actions.FUNCTIONS.Build_Barracks_screen("now", (7, 30))
              else:
                return actions.FUNCTIONS.Build_Barracks_screen("now", (7, 40))
            else:
              if len(barracks)==0:
                return actions.FUNCTIONS.Build_Barracks_screen("now", (75, 10))
              elif len(barracks)==1:
                return actions.FUNCTIONS.Build_Barracks_screen("now", (75, 20))
              elif len(barracks)==2:
                return actions.FUNCTIONS.Build_Barracks_screen("now", (75, 30))
              else:
                return actions.FUNCTIONS.Build_Barracks_screen("now", (75, 40))

        # Gets the array of SCVs on screen
        scvs = self.get_units_by_type(obs,units.Terran.SCV)
        if len(scvs) > 0:
          # Choose a SCV
          scvs = random.choice(scvs)
          # Action of selecting a SCV
          return actions.FUNCTIONS.select_point("select_all_type", (scvs.x, scvs.y))

    # Build the supply depots
    if len(supply_depots) < 5 and minerals > 150:
      # Verifies that an SCV is selected
      if self.unit_type_is_selected(obs, units.Terran.SCV):
        # Verifies that the action is available on screen
        if self.can_do(obs,actions.FUNCTIONS.Build_SupplyDepot_screen.id):
          # Here we use the flag abajo in order to see our position and
          # get the cordinates for our barracks
          if self.abajo:
            # Actions of Building supply depots in specific coordinate depending
            # on which number of supply depot it is
            if len(supply_depots)==1:
              return actions.FUNCTIONS.Build_SupplyDepot_screen("now", (5, 60))
            elif len(supply_depots)==2:
              return actions.FUNCTIONS.Build_SupplyDepot_screen("now", (12, 60))
            elif len(supply_depots)==3:
              return actions.FUNCTIONS.Build_SupplyDepot_screen("now", (5, 53))
            else:
              return actions.FUNCTIONS.Build_SupplyDepot_screen("now", (12, 53))
          else:
            if len(supply_depots)==1:
              return actions.FUNCTIONS.Build_SupplyDepot_screen("now", (73, 60))
            elif len(supply_depots)==2:
              return actions.FUNCTIONS.Build_SupplyDepot_screen("now", (80, 60))
            elif len(supply_depots)==3:
              return actions.FUNCTIONS.Build_SupplyDepot_screen("now", (73, 53))
            else:
              return actions.FUNCTIONS.Build_SupplyDepot_screen("now", (80, 53))

      # Verifles if there is a worker doing nothing to select him
      if actions.FUNCTIONS.select_idle_worker.id in obs.observation["available_actions"]:
        # Action of selecting a SCV
        return actions.FUNCTIONS.select_idle_worker("select")
      else:
          # Get array of SCVs on screen
          scvs = self.get_units_by_type(obs,units.Terran.SCV)
          if len(scvs) > 0:
            # Choose a random SCV
            scvs = random.choice(scvs)
            # Action of selectin a SCV
            return actions.FUNCTIONS.select_point("select_all_type", (scvs.x, scvs.y))

    # Gets the array of SCV's on screen
    scvs = self.get_units_by_type(obs, units.Terran.SCV)
    # Gets the array of Command Centers on screen
    command_center = self.get_units_by_type(obs, units.Terran.CommandCenter)
    # Train SCVs
    if len (scvs) < 16:
      # Verifies if Command Center is selected
      if self.unit_type_is_selected(obs, units.Terran.CommandCenter):
        # Verifies that the action is available on screen
        if self.can_do(obs, actions.FUNCTIONS.Train_SCV_quick.id):
          # Action of training SCV
          return actions.FUNCTIONS.Train_SCV_quick("now")

      # Gets the array of Command Centers on screen
      command_center = self.get_units_by_type(obs, units.Terran.CommandCenter)
      # Verifies that there is at least one command center
      if len(command_center) > 0:
        # Choose a random command center
        command_center = random.choice(command_center)
        # Action of selecting a command center
        return actions.FUNCTIONS.select_point("select_all_type", (
                                                command_center.x,
                                                command_center.y))

    # Action of doing nothing until next step
    return actions.FUNCTIONS.no_op()

def main(unused_argv):
  agent = TerranAgent()

  try:
    while True:
      with sc2_env.SC2Env(
          map_name="Simple128",
          players=[sc2_env.Agent(sc2_env.Race.terran),
                   sc2_env.Bot(sc2_env.Race.zerg,
                               sc2_env.Difficulty.hard)],
          agent_interface_format=features.AgentInterfaceFormat(
              feature_dimensions=features.Dimensions(screen=84, minimap=64),
              use_feature_units=True),
          step_mul=16,
          game_steps_per_episode=0,
          visualize=True) as env:

        agent.setup(env.observation_spec(), env.action_spec())

        timesteps = env.reset()
        agent.reset()

        while True:
          step_actions = [agent.step(timesteps[0])]
          if timesteps[0].last():
            break
          timesteps = env.step(step_actions)

  except KeyboardInterrupt:
    pass

if __name__ == "__main__":
  app.run(main)
