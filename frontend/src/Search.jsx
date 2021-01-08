import React from 'react';

import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import ImageIcon from '@material-ui/icons/Image';
import VideoLibraryIcon from '@material-ui/icons/VideoLibrary';
import SearchIcon from "@material-ui/icons/Search";
import MenuBookIcon from '@material-ui/icons/MenuBook';

import { makeStyles } from '@material-ui/core/styles';
import {
  FormControl,
  TextField,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Button,
  InputAdornment,
  Typography,
  Container,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@material-ui/core';

import ResultItem from "./ResultItem";
import theme from "./theme";


const useStyles = makeStyles((theme) => ({
  heading: {
    fontSize: theme.typography.pxToRem(15),
    fontWeight: theme.typography.fontWeightRegular,
  },
  searchButton: {
    height: "57px"
  },
  rangeSelect: {
    height: "39px"
  }
}));

export default function Search() {
  const classes = useStyles();
  const [searchAccuracy, setSearchAccuracy] = React.useState('or');
  const handleSearchAccuracyChange = (event) => {
    setSearchAccuracy(event.target.value);
  };

  const [searchRange, setSearchRange] = React.useState('image');
  const handleSearchRangeChange = (event) => {
    setSearchRange(event.target.value);
  };

  const testImageURL = "https://raw.githubusercontent.com/TsingJyujing/blogs/master/img/2020-07-07-12-28-05.png";
  const postExample = {
    title: "Test Post Block",
    date: "2020-01-01",
    description: "Details of the POST block",
    image: testImageURL,
    url: testImageURL,
  }

  const [searchKeywords, setSearchKeywords] = React.useState("");

  const handleSearchKeywords = (event) => {
    setSearchKeywords(event.target.value);
  };

  const [searchResults, setSearchResults] = React.useState([]);

  const handleClickSearch = () => {
    // TODO get data from backend and update list
    setSearchResults(
      searchResults.concat([postExample])
    );
  }

  const handleTextKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleClickSearch()
    }
  }
  // TODO execute search if the parameter q in address

  return (
    <Container maxWidth="lg">
      <br />
      <Grid container spacing={3}>
        <Grid item xs={10}>
          <TextField
            variant="filled"
            className={{
              margin: theme.spacing(1),
            }}
            id="search-keywords"
            label="Search"
            fullWidth
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Select
                    id="search-range"
                    value={searchRange}
                    onChange={handleSearchRangeChange}
                    className={classes.rangeSelect}
                  >
                    <MenuItem value={"image"}><ImageIcon /></MenuItem>
                    <MenuItem value={"video"}><VideoLibraryIcon /></MenuItem>
                    <MenuItem value={"novel"}><MenuBookIcon /></MenuItem>
                  </Select>
                </InputAdornment>
              )
            }}
            value={searchKeywords}
            onChange={handleSearchKeywords}
            onKeyPress={handleTextKeyPress}
          >
          </TextField>
        </Grid>
        <Grid item xs={2}>
          <Button variant="contained" color="primary" fullWidth className={classes.searchButton} onClick={handleClickSearch}>
            <SearchIcon />
          </Button>
        </Grid>
        <Grid item xs={12} sm={12}>
          <Accordion>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              aria-controls="panel1a-content"
              id="panel1a-header"
            >
              <Typography className={classes.heading}>Advanced Search</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid item xs={12} md={6} sm={6}>
                <FormControl fullWidth>
                  <InputLabel id="search-accuracy-select-label">Search Accuracy</InputLabel>
                  <Select
                    labelId="search-accuracy-select-label"
                    id="search-accuracy"
                    value={searchAccuracy}
                    onChange={handleSearchAccuracyChange}
                  >
                    <MenuItem value={"or"}>Or</MenuItem>
                    <MenuItem value={"andmaybe"}>And Maybe</MenuItem>
                    <MenuItem value={"and"}>And</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>
      </Grid>
      <Grid container spacing={3}>
        {searchResults.map((post) => (
          <ResultItem key={post.title} post={post} />
        ))}
      </Grid>
    </Container>
  );
}
