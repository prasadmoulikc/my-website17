document.addEventListener("DOMContentLoaded", function () {

  // These values come from admin.html via window variables
  const feedbackData = window.FEEDBACK_DATA || [0, 0, 0];
  const moodLabels = Object.keys(window.MOOD_DATA || {});
  const moodValues = Object.values(window.MOOD_DATA || {});

  // Feedback Pie Chart
  new Chart(document.getElementById("feedbackChart"), {
    type: "pie",
    data: {
      labels: ["Helpful (5)", "Okay (3)", "Poor (1)"],
      datasets: [{
        data: feedbackData,
        backgroundColor: ["#00e676", "#ffeb3b", "#ff5252"]
      }]
    }
  });

  // Mood Bar Chart
  new Chart(document.getElementById("moodChart"), {
    type: "bar",
    data: {
      labels: moodLabels,
      datasets: [{
        label: "Mood Count",
        data: moodValues,
        backgroundColor: "#00e6e6"
      }]
    }
  });

});
