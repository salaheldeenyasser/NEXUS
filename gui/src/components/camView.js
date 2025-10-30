import videoTest from "../media/nig.mp4";
import classes from '../styles/camView.module.css'
import { useNavigate } from "react-router-dom";

export default function CamView() {
    const navigate = useNavigate();


    const goHome = () => {
        navigate('/');
    }
    return(
        <div>
            <video src={videoTest} autoPlay loop muted className={classes.camVid}></video>
            <button onClick={goHome} className={classes.camHome}>Home</button>
        </div>
    )
}