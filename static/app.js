var app = new Vue({
  el: 'div#app',
  data: {
    files: {},
    error: "",
    current_track: "",
  },
  methods: {
    playOrBrowse: function (file) {
      if (file.type == 'dir') {
        app.getBrowsableList(file.path)
      } else if (file.type == 'file') {
        if (app.current_track != "") {
          var aud = document.querySelector("audio.player");
          aud.stop()
        }
        app.current_track = file.path
      } else {
        app.error = "Unexpected type: " + file.type
      }
    },
    getBrowsableList: function (path) {
      encodedPath = encodeURIComponent(path);
      fetch("/api/v1/browse?path=" + encodedPath)
        .then(response => {
          return response.json()
        })
        .then(data => {
          results = JSON.parse(data);
          if(!("error" in results)) {
            app.files = results
          } else {
            app.error = results.error
          }
        })
        .catch(err => {
          console.log(err)
        })
    },
    handlePlayer: function () {
      var aud = document.querySelector("audio.player");
      aud.play()
      aud.onended = function() {
        app.current_track = ""
      }
    }
  }
})

app.getBrowsableList(path='/');
