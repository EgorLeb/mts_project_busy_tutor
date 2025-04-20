import { useDispatch, useSelector } from "react-redux";
import { TimeSlotBooking } from "./TimeSlotBooking";
import { useEffect, useState } from "react";
import axios from "axios";
import { link } from "../../components/Calendar/Constants";
import { setTutor } from "../../store/slices/ModalSlice";
import { setStatuses } from "../../store/slices/StatusSlice";

export const Timeslots = () => {
  const daysOfWeek = useSelector((state) => state.dateReducer.daysOfWeek);

  const statuses = useSelector((state) => state.statusReducer.statuses);

  const [timeslots, setTimeslots] = useState([]);

  useEffect(() => {
    setTimeslots(
      new Array(24 * 7).fill(null).map((_, index) => {
        const dayIndex = index % 7;
        const hour = Math.floor(index / 7);
        const date = daysOfWeek[dayIndex];
        const formattedHour = `${hour.toString().padStart(2, "0")}`;
        return [date, formattedHour];
      })
    );
  }, [daysOfWeek]);

  const dispatch = useDispatch();

  useEffect(() => {

    const getInfoTeacher = async () => {
    const data = {};
    data.type = "getInfo";
    data.mail = JSON.parse(localStorage.getItem("ownerMail"));
    console.log(data);
    axios
      .post(link, data)
      .then((response) => {
        console.log(response.data);
        dispatch(setTutor(response.data.fullname));
      })
      .catch((reason) => {
        if (reason.response) {
          console.log(reason.response.status);
        } else if (reason.request) {
          console.log(reason.response.status);
        }
      });
    };

    const getStatuses = async () => {
    console.log("[getTime START] statuses", statuses);
    const data = {};
    data.type = "getTime";
    if (JSON.parse(localStorage.getItem("role")) === "owner") {
      data.ownerMail = JSON.parse(localStorage.getItem("mail"));
    } else {
      data.ownerMail = JSON.parse(localStorage.getItem("ownerMail"));
    }
    console.log("[getTime START] data", data);
    axios
      .post(link, data)
      .then((response) => {
        console.log("[getTime START] response", response.data);
        dispatch(
          setStatuses({
            free_slots: JSON.parse(response.data.freeSlots),
            busy_slots: JSON.parse(response.data.busySlots),
          })
        );
      })
      .catch((reason) => {
        console.log("Error in getStatuses");
        if (reason.response) {
          if (reason.response.status === 406) {
            // alert("This user is alredy exist. Please log in")
          } else if (reason.response.status === 405) {
          }
          console.log(reason.response.status);
        } else if (reason.request) {
          console.log(reason.response.status);
        }
      });

    console.log("[getTime END] statuses", statuses);
    console.log("[getTime END] data", data);

  };

    if (JSON.parse(localStorage.getItem("role")) === "visitor") {
      console.log("test");
      getInfoTeacher();
    }

    getStatuses();
    console.log("[getInfo and getTime END] statuses: ", statuses);
  }, [dispatch, daysOfWeek]);


  useEffect(() => {
    console.log("[setTime START] statuses", statuses);

    if (
      Object.keys(statuses.free_slots).length === 0 &&
      Object.keys(statuses.busy_slots).length === 0
    ) {
      return;
    }

    const data = {
      type: "setTime",
      mail:
        JSON.parse(localStorage.getItem("role")) === "owner"
          ? JSON.parse(localStorage.getItem("mail"))
          : JSON.parse(localStorage.getItem("ownerMail")),
      password: JSON.parse(localStorage.getItem("password")),
      freeSlots: JSON.stringify(
        statuses.free_slots !== undefined ? statuses.free_slots : {}
      ),
      busySlots: JSON.stringify(
        statuses.busy_slots !== undefined ? statuses.busy_slots : {}
      ),
    };

    axios
      .post(link, data)
      .then((response) => console.log(response.data))
      .catch((error) => {
        console.log(error);
      });

    console.log("[setTime END] data: ", data);
    console.log("[setTime END] statuses: ", statuses);
  }, [statuses]);


  const checkStatus = (timeslot) => {
    const [date, hour] = timeslot;
    var [day, month, year] = date;

    // console.log(date, hour);

    if (statuses?.["busy_slots"]?.[year]?.[month]?.[day]?.[hour]) {
      // console.log(`${date}, ${hour}: Busy`);
      return [
        "Busy",
        statuses["busy_slots"][year][month][day][hour]["name"],
        statuses["busy_slots"][year][month][day][hour]["phone"],
      ];
    } else if (
      statuses?.["free_slots"]?.[year]?.[month]?.[day]?.includes(hour)
    ) {
      // console.log(`${date}, ${hour}: Free`);
      return ["Free"];
    } else {
      // console.log(`${date}, ${hour}: No slot`);
      return ["No_slot"];
    }
  };

  return (
    <div className="grid grid-cols-7 grid-rows-auto w-full ml-6 mt-4 rounded-sm border-header_border">
      {/* {console.log(timeslots)} */}
      {timeslots.map((timeslot) => (
        <TimeSlotBooking timeslot={timeslot} status={checkStatus(timeslot)} />
      ))}
    </div>
  );
};
