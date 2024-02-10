window.onload = async () => {
    const xhr = new XMLHttpRequest()
    xhr.open("POST", "https://api.python-bale-bot.ir/api/countView")
    xhr.setRequestHeader("Content-Type", "application/json")
    xhr.onload = () => console.log("View was calculated!")
    const data = JSON.stringify({
        websiteAddress: "python-bale-bot-doc",
        ip: await getIP()
    })
    xhr.send(data)
}

async function getIP() {
    return await fetch("https://api.ipify.org/").then((r) => r.text())
}