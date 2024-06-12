---
title: "Kidnapped Robot Problem"
date: 2022-09-10
timeline: 2019-09-31
category: work
tags: ROS C++ OpenCV
organisation: "Epilog d.o.o"
---

During school break in 2019, I had a summer job at [Epilog d.o.o.](https://www.epilog.net/en), a company that develops autonomous warehouse solutions. The IT team I joined was building a robot as well as developing software for its systems. Since I was a student with little experience, I was assigned a side project: Kidnapped Robot Problem.

## Problem

The Kidnapped Robot Problem is a problem of an autonomous robot, where said robot gets 'kidnapped', or lost, which means that the robot is moved by an external force, e.g. someone picks it up and takes it to another spot. The original problem is that the robot suddenly finds itself in an unknown environment, and needs to find its location in it. In my case, I focused only on the problem where the environment is known, but the location of the robot is not.

## Alternative solutions

At that time we used Advanced Monte Carlo Localization, [AMCL](http://wiki.ros.org/amcl), which is a probabilistic algorithm that determines the location of the robot in a known map and uses the robot's movement as well as the environment it sees to determine the robot's position. It is better than just using odometry because just a few millimetres of error can accumulate over time and the position of the robot is not precise. If a robot is suddenly moved, AMCL eventually recognizes that the robot is not where it should be, and after a while, it converges to the robot's new correct location. This requires the robot to move around in an, now unknown, environment, and usually took around a minute or two of mindlessly driving around.

Another method I found was localization using Wi-Fi signal strength. The idea is to have multiple Wi-Fi routers around the environment, and have their location known. For precise localization at least three points are needed. The robot then localizes itself with the help of Wi-Fi signal strength. A higher signal means the robot is closer to the router, and vice versa. If the robot can calculate distance from multiple signal sources, it can calculate its rough location, and use AMCL to determine its precise location. I could not try this method, as we only had 1 Wi-Fi router. Another problem we faced was that the distance calculation from signal strength is not as precise as we would like, making it only slightly better than using AMCL alone.

## Solution

I approached the problem from an exploration perspective. If a robot suddenly doesn't know where on the map it is, it can be treated the same as if it finds itself in an unknown environment. That way we can treat the environment as if we have never seen it before, and start to map it from scratch. The core idea is to then compare our newly created map of the environment to the already known map, and try to figure out where the robot is.

Our robot was fitted with a [lidar](https://en.wikipedia.org/wiki/Lidar), which uses a laser to measure distances with a few millimeter-tolerance. It was used for new map generation. The robot ran on Robot Operating System, [ROS](https://www.ros.org/), and the algorithm was written in C++ with [OpenCV](https://opencv.org/). Our robot was also confined to an indoor and closed space, which had QR codes at various locations to help the robot orient itself in it. If such a QR code was seen, the robot immediately knew its precise position in the environment.

I used two services, already written for ROS. The first one is [gmapping](https://wiki.ros.org/gmapping), which maps the environment and localizes the robot within it. The second one is [frontier exploration](http://wiki.ros.org/frontier_exploration), which extracts the edges and unexplored sections of a map. The service I wrote combined both information, and used information about known QR codes in the environment. The algorithm works as follows:

- wait for gmapping to map a new portion of the map,
- use OpenCV's template matching to overlay the newly generated map with a known map,
- from best matches determine where QR codes should be on the newly generated map,
- use frontier exploration's extracted edges and score them according to distance from the robot and to the nearest expected QR code,
- send the coordinates with the highest score to the global planner,
- repeat until the QR code is found.

## Conclusions

The algorithm was tested briefly, as it was a low-priority project, but showed promising results -  the proposed coordinates always pointed in the direction of a QR code. Coordinate sending was also not used, as it would require the modification of the global planner, but the robot was moved manually toward the best coordinates.

<!--A few modifications to the algorithm were required. I was not an experienced programmer back then, and some refactoring would be needed to make my code more efficient.-->

<!--## Today-->