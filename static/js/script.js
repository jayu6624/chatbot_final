async function postData(url = "", data = {}) {
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return response.json(); // Parse response JSON
  } catch (error) {
    console.error("Error:", error);
    throw error; // Rethrow error to propagate it to caller
  }
}

// Assuming 'sendbutton' is your button element and 'question1' and 'solution' are elements on your webpage
sendbutton.addEventListener("click", async () => {
  const questionInput = document.getElementById("questionInput").value;
  document.getElementById("questionInput").value = "";
  document.querySelector(".right").style.display = "none";
  document.querySelector(".right1").style.display = "block";
  question1.innerHTML = questionInput;

  try {
    const result = await postData("/api", { question: questionInput });
    // Access the 'result' field to get the answer
    const answer = result.result;

    // Display the answer on the webpage
    const solutionElement = document.getElementById("solution");
    solutionElement.innerHTML = answer;
  } catch (error) {
    console.error("Error fetching data:", error);
    // Handle error appropriately, e.g., display an error message on the webpage
  }
});
function reloadPage() {
  window.location.reload();
}
