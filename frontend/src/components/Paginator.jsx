import {Button, Grid, MenuItem, Select} from "@material-ui/core";
import BottomNavigation from "@material-ui/core/BottomNavigation";
import BottomNavigationAction from "@material-ui/core/BottomNavigationAction";
import FirstPageIcon from "@material-ui/icons/FirstPage";
import NavigateBeforeIcon from "@material-ui/icons/NavigateBefore";
import Icon from "@material-ui/core/Icon";
import NavigateNextIcon from "@material-ui/icons/NavigateNext";
import React from "react";

export function PaginatorWithCombo({pageId, setPageId, pageCount}){
    const handleChangePageId = (event) => {
        setPageId(event.target.value);
    };
    const handlePreviousPage = () => {
        if (pageId > 1) {
            setPageId(pageId - 1)
        }
    };
    const handleNextPage = () => {
        if (pageId < pageCount) {
            setPageId(pageId + 1);
        }
    }
    return (
        <Grid container spacing={3}>
                      <Grid item spacing={3} xs={4}>
                <Button variant="contained" color={pageId <= 1 ? "default" : "primary"} fullWidth
                        onClick={handlePreviousPage}>
                    <NavigateBeforeIcon/>
                </Button>
            </Grid>
            <Grid item spacing={3} xs={4}>
                <Select
                    id="select-page-id"
                    value={pageId}
                    onChange={handleChangePageId}
                    fullWidth
                >
                    {
                        [...Array(pageCount).keys()].map(
                            i => (<MenuItem value={i + 1}>{`${i + 1} / ${pageCount}`}</MenuItem>)
                        )
                    }
                </Select>
            </Grid>
            <Grid item spacing={3} xs={4}>
                <Button variant="contained" color={pageId >= pageCount ? "default" : "primary"} fullWidth
                        onClick={handleNextPage}>
                    <NavigateNextIcon/>
                </Button>
            </Grid>
        </Grid>
    )
}

export function Paginator({pageId, setPageId}) {
    const modifyPageId = (newPageId) => {
        if (newPageId <= 1) {
            setPageId(1);
        } else {
            setPageId(newPageId);
        }
    };

    return (
        <Grid container spacing={3}>
            <Grid item sm={12} md={12} lg={12} xs={12}>
                <BottomNavigation>
                    <BottomNavigationAction label="First" icon={<FirstPageIcon/>} onClick={() => modifyPageId(1)}/>
                    <BottomNavigationAction label="Previous" icon={<NavigateBeforeIcon/>}
                                            onClick={() => modifyPageId(pageId - 1)}/>
                    <BottomNavigationAction label="Current" icon={<Icon>{pageId}</Icon>} onClick={() => {
                        const pageIdInput = prompt("Please input page num:", `${pageId}`);
                        if (pageIdInput != null) {
                            modifyPageId(parseInt(pageIdInput));
                        }
                    }}/>
                    <BottomNavigationAction label="Next" icon={<NavigateNextIcon/>}
                                            onClick={() => modifyPageId(pageId + 1)}/>
                </BottomNavigation>
            </Grid>
        </Grid>
    );
}