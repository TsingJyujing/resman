import Typography from "@material-ui/core/Typography";
import React from "react";

export default function DescriptionBlock({text, variant = "body1"}) {
    return (
        <Typography gutterBottom variant={variant} gutterBottom>{
            text.split("\n").flatMap(line => {
                return [line, <br/>]
            })
        }</Typography>
    )
}