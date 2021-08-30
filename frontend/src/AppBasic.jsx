import React from 'react';
import {createStyles, makeStyles, useTheme} from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import GitHubIcon from '@material-ui/icons/GitHub';
import Drawer from '@material-ui/core/Drawer';
import Hidden from '@material-ui/core/Hidden';
import {Divider, List, ListItem, ListItemIcon, ListItemText, Menu, MenuItem} from "@material-ui/core";
import clsx from 'clsx';
import {createGetRequestUrl} from "./Utility";
import {searchEntries, utilitiesEntries} from "./Config";


function ItemCollection({entries, title}) {
    return (<List>
        <ListItem><ListItemText primary={title}/></ListItem>
        {entries.map((entry) => {
            return (<ListItem button component="a" key={entry.title} href={entry.url} target={"_blank"}>
                <ListItemIcon>{entry.icon}</ListItemIcon>
                <ListItemText primary={entry.title}/>
            </ListItem>);
        })}
    </List>);
}

const drawerWidth = 240;
const useStyles = makeStyles((theme) =>
    createStyles({
        root: {
            flexGrow: 1,
        },
        appBar: {
            [theme.breakpoints.up('sm')]: {
                width: `100%`,
                marginLeft: drawerWidth,
            },
        },
        appBarShift: {
            width: `calc(100% - ${drawerWidth}px)`,
            marginLeft: drawerWidth,
            transition: theme.transitions.create(['margin', 'width'], {
                easing: theme.transitions.easing.easeOut,
                duration: theme.transitions.duration.enteringScreen,
            }),
        },
        menuButton: {
            marginRight: theme.spacing(2),
        },
        title: {
            flexGrow: 1,
        },
        toolbar: theme.mixins.toolbar,
        drawer: {
            width: drawerWidth,
            flexShrink: 0,
        },
        drawerPaper: {
            width: drawerWidth,
        },
        drawerHeader: {
            display: 'flex',
            alignItems: 'center',
            padding: theme.spacing(0, 1),
            // necessary for content to be below app bar
            ...theme.mixins.toolbar,
            justifyContent: 'flex-end',
        },
        content: {
            flexGrow: 1,
            padding: theme.spacing(3),
            transition: theme.transitions.create('margin', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.leavingScreen,
            }),
            marginLeft: 0,
        },
        contentShift: {
            transition: theme.transitions.create('margin', {
                easing: theme.transitions.easing.easeOut,
                duration: theme.transitions.duration.enteringScreen,
            }),
            marginLeft: 0,
        },
    }),
);

export default function AppBasic(props) {
    const classes = useStyles();
    const theme = useTheme();
    const [anchorEl, setAnchorEl] = React.useState(null);
    const isMenuOpen = Boolean(anchorEl);
    const handleMenuClose = () => {
        setAnchorEl(null);
    };
    const container = window !== undefined ? () => window.document.body : undefined;
    const [drawerOpen, setDrawerOpen] = React.useState(false);
    const handleDrawerToggle = () => {
        setDrawerOpen(!drawerOpen);
    };

    const drawer = (
        <div>
            <div className={classes.toolbar}/>
            <Divider/>
            <ItemCollection entries={searchEntries} title={"Search"}/>
            <Divider/><ItemCollection entries={utilitiesEntries} title={"Utilities"}/>
            <Divider/>
            <List>
                <ListItem button component="a" key="source-code" href="https://github.com/TsingJyujing/resman"
                          target={"_blank"}>
                    <ListItemIcon><GitHubIcon/></ListItemIcon>
                    <ListItemText primary="Source Code"/>
                </ListItem>
            </List>
            <Divider/>
        </div>
    );

    return (
        <div className={classes.root}>
            <AppBar position="fixed" className={clsx(classes.appBar, {
                [classes.appBarShift]: drawerOpen,
            })}>
                <Toolbar>
                    <IconButton edge="start" className={classes.menuButton} color="inherit" aria-label="menu"
                                onClick={handleDrawerToggle}>
                        <MenuIcon/>
                    </IconButton>
                    <Typography variant="h6" className={classes.title}>
                        Resman
                    </Typography>
                </Toolbar>
            </AppBar>
            <nav className={classes.drawer} aria-label="mailbox folders">
                <Hidden smUp implementation="css">
                    <Drawer
                        container={container}
                        variant="temporary"
                        anchor={theme.direction === 'rtl' ? 'right' : 'left'}
                        open={drawerOpen}
                        onClose={handleDrawerToggle}
                        classes={{
                            paper: classes.drawerPaper,
                        }}
                        ModalProps={{
                            keepMounted: true, // Better open performance on mobile.
                        }}
                    >
                        {drawer}
                    </Drawer>
                </Hidden>
            </nav>
            <Menu
                anchorEl={anchorEl}
                anchorOrigin={{vertical: 'top', horizontal: 'right'}}
                id='primary-search-account-menu'
                keepMounted
                transformOrigin={{vertical: 'top', horizontal: 'right'}}
                open={isMenuOpen}
                onClose={handleMenuClose}
            >
                <MenuItem
                    onClick={() => {
                        window.location = createGetRequestUrl(window.location, "/accounts/logout/", {})
                    }}
                >
                    Logout
                </MenuItem>
            </Menu>
            );
            <main className={clsx(classes.content, {
                [classes.contentShift]: drawerOpen,
            })}>
                <div className={classes.drawerHeader}/>
                {props.children}
            </main>
        </div>
    );
}

