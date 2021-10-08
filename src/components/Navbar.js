import { NavLink } from "react-router-dom";

import { NavbarData } from "./NavbarData";
import "./Navbar.css";

function Navbar() {
  return (
    <nav className="nav-menu">
      {NavbarData.map((item, index) => {
        return (
          <NavLink exact to={item.path} key={index} className="nav-text" activeClassName="active">
            {item.icon}
            <span>{item.title}</span>
          </NavLink>
        )
      })}
    </nav>
  )
}

export default Navbar
