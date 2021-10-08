function PageNotFound(props) {
  return (
    <p>Page {props.match.url} not found</p>
  );
}

export default PageNotFound;