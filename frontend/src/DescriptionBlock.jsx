import Typography from "@material-ui/core/Typography";
import React from "react";
import {RegExpReplace} from "./Utility";

export default function DescriptionBlock({text, variant = "body1"}) {
    return (
        <Typography gutterBottom variant={variant} gutterBottom>{
            text.split(/(\n|\s)+/).flatMap(line => {
                return [line, <br/>]
            })
        }</Typography>
    )
}