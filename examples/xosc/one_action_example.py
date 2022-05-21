"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.
  
    Simple example showing how one vehicle triggers based on distance from another, then keeps distance to that car

    Some features used:
    - LongitudinalDistanceAction

    - TimeHeadwayCondition

"""
import os
from scenariogeneration import xosc, prettyprint

### create catalogs
catalog = xosc.Catalog()
catalog.add_catalog("VehicleCatalog", "../xosc/Catalogs/Vehicles")


### create road
road = xosc.RoadNetwork(
    roadfile="../xodr/e6mini.xodr", scenegraph="../models/e6mini.osgb"
)


### create parameters
paramdec = xosc.ParameterDeclarations()

paramdec.add_parameter(
    xosc.Parameter("$HostVehicle", xosc.ParameterType.string, "car_white")
)
paramdec.add_parameter(
    xosc.Parameter("$TargetVehicle", xosc.ParameterType.string, "car_red")
)

### create vehicles

bb = xosc.BoundingBox(2, 5, 1.8, 2.0, 0, 0.9)
fa = xosc.Axle(0.523598775598, 0.8, 1.68, 2.98, 0.4)
ba = xosc.Axle(0.523598775598, 0.8, 1.68, 0, 0.4)
white_veh = xosc.Vehicle("car_white", xosc.VehicleCategory.car, bb, fa, ba, 69, 10, 10)

white_veh.add_property_file("../models/car_white.osgb")
white_veh.add_property("model_id", "0")


bb = xosc.BoundingBox(1.8, 4.5, 1.5, 1.3, 0, 0.8)
fa = xosc.Axle(0.523598775598, 0.8, 1.68, 2.98, 0.4)
ba = xosc.Axle(0.523598775598, 0.8, 1.68, 0, 0.4)
red_veh = xosc.Vehicle("car_red", xosc.VehicleCategory.car, bb, fa, ba, 69, 10, 10)

red_veh.add_property_file("../models/car_red.osgb")
red_veh.add_property("model_id", "2")

## create entities

egoname = "Ego"
targetname = "Target"

entities = xosc.Entities()
entities.add_scenario_object(egoname, white_veh)
entities.add_scenario_object(targetname, red_veh)


### create init

init = xosc.Init()
step_time = xosc.TransitionDynamics(
    xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1
)

egospeed = xosc.AbsoluteSpeedAction(30, step_time)
egostart = xosc.TeleportAction(xosc.LanePosition(25, 0, -3, 0))

targetspeed = xosc.AbsoluteSpeedAction(40, step_time)
targetstart = xosc.TeleportAction(xosc.LanePosition(15, 0, -2, 0))

init.add_init_action(egoname, egospeed)
init.add_init_action(egoname, egostart)
init.add_init_action(targetname, targetspeed)
init.add_init_action(targetname, targetstart)


### create an event

trigcond = xosc.TimeHeadwayCondition(targetname, 0.1, xosc.Rule.greaterThan)

trigger = xosc.EntityTrigger(
    "mytesttrigger", 0.2, xosc.ConditionEdge.none, trigcond, egoname
)

event = xosc.Event("myfirstevent", xosc.Priority.overwrite)
event.add_trigger(trigger)

sin_time = xosc.TransitionDynamics(
    xosc.DynamicsShapes.linear, xosc.DynamicsDimension.time, 3
)
action = xosc.LongitudinalDistanceAction(
    egoname, max_deceleration=3, max_speed=50, distance=-4
)
event.add_action("newspeed", action)


## create the act,
man = xosc.Maneuver("my_maneuver")
man.add_event(event)

mangr = xosc.ManeuverGroup("mangroup")
mangr.add_actor("$owner")
mangr.add_maneuver(man)
starttrigger = xosc.ValueTrigger(
    "starttrigger",
    0,
    xosc.ConditionEdge.rising,
    xosc.SimulationTimeCondition(0, xosc.Rule.greaterThan),
)
act = xosc.Act("my_act", starttrigger)
act.add_maneuver_group(mangr)

## create the story
storyparam = xosc.ParameterDeclarations()
storyparam.add_parameter(
    xosc.Parameter("$owner", xosc.ParameterType.string, targetname)
)
story = xosc.Story("mystory", storyparam)
story.add_act(act)

## create the storyboard
sb = xosc.StoryBoard(init)
sb.add_story(story)

## create the scenario
sce = xosc.Scenario(
    "adapt_speed_example",
    "Mandolin",
    paramdec,
    entities=entities,
    storyboard=sb,
    roadnetwork=road,
    catalog=catalog,
)

# Print the resulting xml
prettyprint(sce.get_element())

# write the OpenSCENARIO file as xosc using current script name
sce.write_xml(os.path.basename(__file__).replace(".py", ".xosc"))

# uncomment the following lines to display the scenario using esmini
# from scenariogeneration import esmini
# esmini(sce,os.path.join('esmini'))
