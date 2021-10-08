import React from 'react'

import { AiFillHome, AiFillProject } from "react-icons/ai";
import { BsFillPersonFill } from "react-icons/bs"

export const NavbarData = [
  {
    title: "Home",
    path: "/",
    icon: <AiFillHome/>
  },
  {
    title: "About me",
    path: "/about",
    icon: <BsFillPersonFill/>
  },
  {
    title: "Projects",
    path: "/projects",
    icon: <AiFillProject/>
  }
]