var deadline;
var timeLeft;
var FirstTime = true
hidden = document.getElementById("timer").hidden
var eventSource = new EventSource("/sse")

    function getTimeLeft(timeLeft, option = false) {
    hours = Math.floor((timeLeft)/3600)
    minutes = Math.floor((timeLeft-hours*3600)/60)
    seconds = Math.floor(timeLeft-hours*3600-minutes*60)
    minutes = minutes < 10 ? "0" + minutes : minutes
    seconds = seconds < 10 ? "0" + seconds : seconds
    return option ? {hours: parseInt(hours), minutes: parseInt(minutes), seconds: parseInt(seconds)} : {hours, minutes, seconds} 
  }


  function removeColor(className, color) {
    ["hours", "minutes", "seconds"].forEach( (element) => {
        document.getElementById(`${element}_div`).classList.remove(className)
      })
    }

  function updateTimeDivs (timeLeft) {
      var {hours, minutes, seconds} = getTimeLeft(timeLeft)
      document.getElementById("hours_div").innerHTML = hours
      document.getElementById("minutes_div").innerHTML = minutes
      document.getElementById("seconds_div").innerHTML = seconds
      // console.log("smooth")
      // var addedTime = timeLeft - oldTimeLeft;
      // console.log(timeLeft, oldTimeLeft, addedTime)
      // for (var i = 1; i < addedTime; i++) {
      //   // updateTimeDivs(timeLeft = timeLeft - i);
      //   // setTimeout(updateTimeDivs, 1000, timeLeft = timeLeft + i);
      // }
  }

    function updateSmoothly (timeLeft, oldTimeLeft, addedTime) {
        var countersObj = {};
        document.querySelectorAll('.value').forEach( element => {
            countersObj[element.id.replace("_div", "")] = element
        });
        const counters = countersObj;
        const speed = 2000000;
        var oldTimeObj = getTimeLeft(oldTimeLeft, option = true)
        // console.log("oldTimeObj: ", oldTimeObj);
        var {hours, minutes, seconds} = getTimeLeft(timeLeft, option = true)
        // console.log("new: ", hours, minutes, seconds);
        const {_hours, _minutes, _seconds} = {_hours: hours - oldTimeObj.hours, _minutes: minutes - oldTimeObj.minutes, _seconds: seconds - oldTimeObj.seconds}
        // console.log(_hours, _minutes, _seconds)
        Object.entries(counters).forEach(([name, counter]) => {
            var prev_data = null
            // console.log(name, counter, eval(`_${name}`), index)
            const animate = (newValue = null, oldValue = null, oldData = null) => {
                var value = eval(`_${name}`);
                console.log()
                if (newValue != null) {
                    value = newValue
                }

                // console.log("oldValue", oldValue)
                // console.log("oldData: ", oldData)
                const time = 0.01;
                var data = parseInt(counter.innerText) + time;
                if (!prev_data) prev_data = data;
                // console.log(data, value)
                if(data < prev_data + value) {
                  console.log(`data + time: ${data}`)
                  temp_time = Math.ceil(data);
                  // temp_time = Math.ceil(data + time);
                    counter.innerText = temp_time < 10 ? "0" + temp_time : temp_time;
                    setTimeout(animate, 1, value, oldValue, oldData);
                } else if (data == "59" && oldValue != null && oldData != null) {
                    // console.log("here")
                    counter.innerText = "00";
                    prev_data = 0;
                    data = 0;
                    setTimeout(animate, 1, oldData + oldValue);
                } else if (value < 0) {
                    setTimeout(animate, 1, 59 - data, value, data);
                } else {
                    // console.log('last')
                    temp_time = prev_data + value;
                    counter.innerText = temp_time < 10 ? "0" + temp_time : temp_time;
                }
                
            }
            animate();
            });
    }
  eventSource.addEventListener("deadline", function(e) {
    console.log(JSON.parse(e.data))
    deadline = JSON.parse(e.data).deadline
    oldTimeLeft = timeLeft
    timeLeft = deadline - Math.floor(Date.now()/1000)
    var {hours, minutes, seconds} = getTimeLeft(timeLeft)
    if (!FirstTime && !hidden) {
      // updateTimeDivs(timeLeft);
      var addedTime = timeLeft - oldTimeLeft;
      console.log(oldTimeLeft, timeLeft, addedTime);
      if (addedTime > 0) {
        updateSmoothly(timeLeft, oldTimeLeft, addedTime);
      ["hours", "minutes", "seconds"].forEach( (element) => {
        document.getElementById(`${element}_div`).classList.add("added_time")
      });
      setTimeout(removeColor, 1000, 'added_time', 'green');
        } else {
            updateTimeDivs(timeLeft);
            ["hours", "minutes", "seconds"].forEach( (element) => {
            document.getElementById(`${element}_div`).classList.add("subbed_time")
        });
        setTimeout(removeColor, 1000, 'subbed_time', 'yellow');
            }
    } else {
      FirstTime = false
    }
    console.log(hours, minutes, seconds)
    console.log("update!")
  }, false)

  eventSource.addEventListener("message", function(e) {
    console.log(e.data)
  }, true)

  // window.onload = function() {
  //   timeLeft = deadline - Math.floor(Date.now()/1000)
  // }
  var animated = false
  setInterval(() => {
    if (!animated) {
      timeLeft = deadline - Math.floor(Date.now()/1000)
      if(timeLeft >= 0) {
        updateTimeDivs(timeLeft)
        if (timeLeft < 60) {
          ["hours", "minutes", "seconds"].forEach( (element) => {
            document.getElementById(`${element}_div`).classList.add("last_time")
          })
          setTimeout(removeColor, 500, 'last_time', 'red')
        }
      } else if (!hidden) {
        // hidden = document.getElementById("timer").hidden = true;
        // document.getElementById("time_up").hidden = false;
        hidden = true
        document.getElementById("hours_div").innerHTML = "0:"
        document.getElementById("minutes_div").innerHTML = "00:"
        document.getElementById("seconds_div").innerHTML = "00"
      }
    } 
  }, 1000);


