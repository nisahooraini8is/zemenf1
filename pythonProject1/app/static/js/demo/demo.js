type = ['primary', 'info', 'success', 'warning', 'danger'];

demo = {
  initPickColor: function() {
    $('.pick-class-label').click(function() {
      var new_class = $(this).attr('new-class');
      var old_class = $('#display-buttons').attr('data-class');
      var display_div = $('#display-buttons');
      if (display_div.length) {
        var display_buttons = display_div.find('.btn');
        display_buttons.removeClass(old_class);
        display_buttons.addClass(new_class);
        display_div.attr('data-class', new_class);
      }
    });
  },
  initDocChart: function() {
    chartColor = "#FFFFFF";
  },
  initDashboardPageCharts: function() {

//DealChart

console.log(dataFromServer.reopendeals, "dataFromServer.reopendeals");

function filterDataByDatedeal(dataArray) {
  const todaydeal = new Date().toISOString().slice(0, 10);
  return dataArray.filter(item => item.date.replace(/[\s,]+/g, '-') === todaydeal);
}

const reopendealstodayData = filterDataByDatedeal(dataFromServer.reopendeals);

function filterDataByYesterdaydeal(dataArray) {
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayFormatted = yesterday.toISOString().slice(0, 10);

  return dataArray.filter(item => item.date.replace(/[\s,]+/g, '-') === yesterdayFormatted);
}

const reopendealsyesterdayData = filterDataByYesterdaydeal(dataFromServer.reopendeals);

function filterDataByLastNDaysdeal(dataArray, n) {
  const currentDate = new Date();
  const filteredData = [];
  for (let i = 0; i <= n; i++) {
    const day = new Date(currentDate);
    day.setDate(currentDate.getDate() - i);
    const dayFormatted = day.toISOString().slice(0, 10);
    const dayData = dataArray.filter(item => item.date.replace(/[\s,]+/g, '-') === dayFormatted);
    filteredData.push(...dayData);
  }

  return filteredData;
}

const daysToFilterdeal = 3;

const reopendealsLast3DaysData = filterDataByLastNDaysdeal(dataFromServer.reopendeals, daysToFilterdeal);

const dateFilterdealDropdown = document.getElementById("dateFilterfordeal");
dateFilterdealDropdown.addEventListener("change", handleDateFilterdeal);

const customDateFormfordeal = document.getElementById("customDateFormfordeal");
customDateFormfordeal.addEventListener("submit", handleCustomDateFilterdeal);

const usernameFilterdealDropdown = document.getElementById("selectUsernamefordeal");
usernameFilterdealDropdown.addEventListener("change", handleUsernameFilterdeal);

const reopendealsData = dataFromServer.reopendeals;

const sumCountsByUsername2 = (dataArray) => {
  const result = {};
  dataArray.forEach(item => {
    const { user_name, count } = item;
    result[user_name] = (result[user_name] || 0) + parseInt(count);
  });
  return result;
};

const reopendealsSummedData = sumCountsByUsername2(reopendealsData);

var dealctx = document.getElementById("DealChart").getContext("2d");
var myChartdeal = new Chart(dealctx, {
  type: 'bar',
  responsive: true,
  legend: {
    display: false
  },
  data: {
    labels: dataFromServer.usernames,
    datasets: [
      {
        label: "Reopendeals",
        backgroundColor: '#9ea60d', // Green color with transparency
        hoverBackgroundColor: '#9ea60d',
        borderColor: '#9ea60d',
        data: dataFromServer.usernames.map(username => reopendealsSummedData[username] || 0),
        barPercentage: 0.3,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    tooltips: {
      enabled: true,
    },
    scales: {
      xAxes: [
        {
          ticks: {
            maxRotation: 90, // Adjust the rotation angle as needed
            minRotation: 10,
          },
          gridLines: {
            display: false, // Remove the grid lines
          },
          barPercentage: 0.7, // Adjust the bar width as needed
          categoryPercentage: 0.6,
        },
      ],
    },
    plugins: {
      labels: false, // Disable rendering labels
    },
  },
});

// Filter data by custom date range
function filterDataByCustomRangedeal(dataArray, startDate, endDate) {
  return dataArray.filter(item => {
    const formattedItemDate = item.date.replace(/[\s,]+/g, '-');
    return formattedItemDate >= startDate && formattedItemDate <= endDate;
  });
}

// Filter data by username
function filterDataByUsernamedeal(dataArray, username) {
  return dataArray.filter(item => item.user_name === username);
}

function updateChartdeal(reopendealsData) {
  const usernames = dataFromServer.usernames;
  const datasetCount = usernames.length;

  const reopendealsCounts = new Array(datasetCount).fill(0);

  // Check if the input data is an array
  if (Array.isArray(reopendealsData)) {
    for (let i = 0; i < datasetCount; i++) {
      const username = usernames[i];

      for (const item of reopendealsData) {
        if (item.user_name === username) {
          reopendealsCounts[i] += parseInt(item.count);
        }
      }
    }
  } else if (typeof reopendealsData === 'object' && reopendealsData !== null) {
    for (let i = 0; i < datasetCount; i++) {
      const username = usernames[i];

      reopendealsCounts[i] = parseInt(reopendealsData[username]) || 0;
    }
  }

  myChartdeal.data.datasets[0].data = reopendealsCounts;
  myChartdeal.update();
}

function handleDateFilterdeal() {
  const selectedValue = dateFilterdealDropdown.value;
  customDateFormfordeal.style.display = 'none';
  if (selectedValue === "select2") {
    if (reopendealsSummedData) {
      updateChartdeal(reopendealsSummedData);
    }
  } else if (selectedValue === "all2") {
    updateChartdeal(reopendealstodayData);
  } else if (selectedValue === "yesterday2") {
    updateChartdeal(reopendealsyesterdayData);
  } else if (selectedValue === "last3days2") {
    updateChartdeal(reopendealsLast3DaysData);
  } else if (selectedValue === "custom2") {
    customDateFormfordeal.style.display = 'block';
  }
}

function handleCustomDateFilterdeal(event) {
  customDateFormfordeal.style.display = 'none';
  event.preventDefault();
  const startDate = document.getElementById("startDate2").value;
  const endDate = document.getElementById("endDate2").value;
  const customReopendealsData = filterDataByCustomRangedeal(dataFromServer.reopendeals, startDate, endDate);
  updateChartdeal(customReopendealsData);
}

function handleUsernameFilterdeal(event) {
  const selectedUsername = event.target.value;
  const selectedDateFilter = dateFilterdealDropdown.value;
  if (selectedUsername === "No filter") {
    if (selectedDateFilter === "yesterday2") {
      updateChartdeal(reopendealsyesterdayData);
    } else if (selectedDateFilter === "last3days2") {
      updateChartdeal(reopendealsLast3DaysData);
    } else if (selectedDateFilter === "custom2") {
      const startDate = document.getElementById("startDate2").value;
      const endDate = document.getElementById("endDate2").value;
      const customReopendealsData = filterDataByCustomRangedeal(dataFromServer.reopendeals, startDate, endDate);
      updateChartdeal(customReopendealsData);
    } else {
      updateChartdeal(reopendealsSummedData);
    }
  } else {
    if (selectedDateFilter === "yesterday2") {
      var userDataRReopendealsYesterday = reopendealsyesterdayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      updateChartdeal(userDataRReopendealsYesterday);
    } else if (selectedDateFilter === "last3days2") {
      var userDataRReopendealsLast3Days = reopendealsLast3DaysData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      updateChartdeal(userDataRReopendealsLast3Days);
    } else if (selectedDateFilter === "custom2") {
      const startDate = document.getElementById("startDate2").value;
      const endDate = document.getElementById("endDate2").value;
      var customUserDataReopendeals = dataFromServer.reopendeals.filter(function(item) {
        var formattedItemDate = item.date.replace(/[\s,]+/g, '-');
        return formattedItemDate >= startDate && formattedItemDate <= endDate && item.user_name === selectedUsername;
      });
      updateChartdeal(customUserDataReopendeals);
    } else {
      var userDataReopendeals = reopendealsSummedData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      updateChartdeal(userDataReopendeals);
    }
  }
}
//candidateChart

console.log(dataFromServer.interviews, "dataFromServer.interviews");

function filterDataByDate(dataArray) {
  const today = new Date().toISOString().slice(0, 10);
  return dataArray.filter(item => item.date.replace(/[\s,]+/g, '-') === today);
}

const interviewstodayData = filterDataByDate(dataFromServer.interviews);

function filterDataByYesterday(dataArray) {
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayFormatted = yesterday.toISOString().slice(0, 10);

  return dataArray.filter(item => item.date.replace(/[\s,]+/g, '-') === yesterdayFormatted);
}

const interviewsyesterdayData = filterDataByYesterday(dataFromServer.interviews);

function filterDataByLastNDays(dataArray, n) {
  const currentDate = new Date();
  const filteredData = [];

  for (let i = 0; i <= n; i++) {
    const day = new Date(currentDate);
    day.setDate(currentDate.getDate() - i);
    const dayFormatted = day.toISOString().slice(0, 10);
    const dayData = dataArray.filter(item => item.date.replace(/[\s,]+/g, '-') === dayFormatted);
    filteredData.push(...dayData);
  }

  return filteredData;
}

const daysToFilter = 3;
const interviewsLast3DaysData = filterDataByLastNDays(dataFromServer.interviews, daysToFilter);

const dateFilterDropdown = document.getElementById("dateFilterforcan");
dateFilterDropdown.addEventListener("change", handleDateFilter);

const customDateFormforcan = document.getElementById("customDateFormforcan");
customDateFormforcan.addEventListener("submit", handleCustomDateFilter);

const usernameFilterDropdown = document.getElementById("selectUsernamefor");
usernameFilterDropdown.addEventListener("change", handleUsernameFilter);

const interviewData = dataFromServer.interviews;

const sumCountsByUsername = (dataArray) => {
  const result = {};
  dataArray.forEach(item => {
    const { user_name, count } = item;
    result[user_name] = (result[user_name] || 0) + parseInt(count);
  });
  return result;
};

const interviewsSummedData = sumCountsByUsername(interviewData);

var candidatectx = document.getElementById("candidateChart").getContext("2d");
var myChartcandidate = new Chart(candidatectx, {
  type: 'bar',
  responsive: true,
  legend: {
    display: false
  },
  data: {
    labels: dataFromServer.usernames,
    datasets: [
      {
        label: "Interviews",
        backgroundColor: '#9ea60d',
        hoverBackgroundColor: '#9ea60d',
        borderColor: '#9ea60d',
        data: dataFromServer.usernames.map(username => interviewsSummedData[username] || 0),
        barPercentage: 0.3,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    tooltips: {
      enabled: true,
    },
    scales: {
      xAxes: [
        {
          ticks: {
            maxRotation: 90, // Adjust the rotation angle as needed
            minRotation: 10,
          },
          gridLines: {
            display: false, // Remove the grid lines
          },
          barPercentage: 0.7, // Adjust the bar width as needed
          categoryPercentage: 0.6,
        },
      ],
    },
    plugins: {
      labels: false, // Disable rendering labels
    },
  },
});

function filterDataByCustomRange(dataArray, startDate, endDate) {
  return dataArray.filter(item => {
    const formattedItemDate = item.date.replace(/[\s,]+/g, '-');
    return formattedItemDate >= startDate && formattedItemDate <= endDate;
  });
}

function filterDataByUsername(dataArray, username) {
  return dataArray.filter(item => item.user_name === username);
}

function updateChartcandi(interviewData) {
  const usernames = dataFromServer.usernames;
  const datasetCount = usernames.length;

  const interviewsCounts = new Array(datasetCount).fill(0);

  // Check if the input data is an array
  if (Array.isArray(interviewData)) {
    for (let i = 0; i < datasetCount; i++) {
      const username = usernames[i];

      for (const item of interviewData) {
        if (item.user_name === username) {
          interviewsCounts[i] += parseInt(item.count);
        }
      }
    }
  } else if (typeof interviewData === 'object' && interviewData !== null) {
    for (let i = 0; i < datasetCount; i++) {
      const username = usernames[i];

      interviewsCounts[i] = parseInt(interviewData[username]) || 0;
    }
  }

  myChartcandidate.data.datasets[0].data = interviewsCounts;
  myChartcandidate.update();
}

function handleDateFilter() {
  const selectedValue = dateFilterDropdown.value;
  customDateFormforcan.style.display = 'none';

  if (selectedValue === "select1") {
    if (interviewsSummedData) {
      updateChartcandi(interviewsSummedData);
    }
  } else if (selectedValue === "all1") {
    updateChartcandi(interviewstodayData);
  } else if (selectedValue === "yesterday1") {
    updateChartcandi(interviewsyesterdayData);
  } else if (selectedValue === "last3days1") {
    updateChartcandi(interviewsLast3DaysData);
  } else if (selectedValue === "custom1") {
    customDateFormforcan.style.display = 'block';
  }
}

function handleCustomDateFilter(event) {
  customDateFormforcan.style.display = 'none';
  event.preventDefault();
  const startDate = document.getElementById("startDate1").value;
  const endDate = document.getElementById("endDate1").value;
  const customInterviewsData = filterDataByCustomRange(dataFromServer.interviews, startDate, endDate);
  updateChartcandi(customInterviewsData);
}

function handleUsernameFilter(event) {
  const selectedUsername = event.target.value;
  const selectedDateFilter = dateFilterDropdown.value;

  if (selectedUsername === "No filter") {
    if (selectedDateFilter === "yesterday1") {
      updateChartcandi(interviewsyesterdayData);
    } else if (selectedDateFilter === "last3days1") {
      updateChartcandi(interviewsLast3DaysData);
    } else if (selectedDateFilter === "custom1") {
      const startDate = document.getElementById("startDate1").value;
      const endDate = document.getElementById("endDate1").value;
      const customInterviewsData = filterDataByCustomRange(dataFromServer.interviews, startDate, endDate);
      updateChartcandi(customInterviewsData);
    } else {
      updateChartcandi(interviewsSummedData);
    }
  } else {
    if (selectedDateFilter === "yesterday1") {
      const userDataYesterday = interviewsyesterdayData.filter(item => item.user_name === selectedUsername);
      updateChartcandi(userDataYesterday);
    } else if (selectedDateFilter === "last3days1") {
      const userDataLast3Days = interviewsLast3DaysData.filter(item => item.user_name === selectedUsername);
      updateChartcandi(userDataLast3Days);
    } else if (selectedDateFilter === "custom1") {
      const startDate = document.getElementById("startDate1").value;
      const endDate = document.getElementById("endDate1").value;
      const customUserData = dataFromServer.interviews.filter(item => {
        const formattedItemDate = item.date.replace(/[\s,]+/g, '-');
        return formattedItemDate >= startDate && formattedItemDate <= endDate && item.user_name === selectedUsername;
      });
      updateChartcandi(customUserData);
    }
  }
}

}
}