import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import Navbar from "./components/Navbar";

import Home from "./pages/Home";
import About from "./pages/About";
import Projects from "./pages/Projects";
import PageNotFound from "./pages/PageNotFound";

import "./App.css";

function App() {
  return (
    <div className="App">
      <h1>My web page</h1>
      <p>TODO short about myself</p>
      <Router>
        <Navbar/>
        <Switch>
          <Route path="/" exact component={Home}/>
          <Route path="/about" component={About}/>
          <Route path="/projects" component={Projects}/>
          <Route path="*" component={PageNotFound}/>
        </Switch>
      </Router>
    </div>
  );
}

export default App;
