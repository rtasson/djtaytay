Vue.component('player', {
  props: ['track'],
  template: `
    <audio controls class="player" v-on:loadstart="handlePlayer()">
      <source v-bind:src="'/play?path=' + track" type="audio/webm">
    </audio>
  `,
  data: function () {
    return {
      handlePlayer: function () {
        var aud = document.querySelector("audio.player");
        aud.play()
        aud.onended = function() {
          app.current_track = ""
        }
      }
    }
  }
})

Vue.component('file', {
  props: ['file'],
  template: `
           <li>
              <a v-on:click="playOrBrowse(file)">{{ file.name }}</a>
           </li>`,
  data: function () {
    return {
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
      }
    }
  }
})

var app = new Vue({
  el: 'div#app',
  data: {
    files: {},
    error: "",
    current_track: "",
  },
  methods: {
    getBrowsableList: function (path) {
      encodedPath = encodeURIComponent(path);
      fetch("/browse?path=" + encodedPath)
        .then(response => {
          return response.json()
        })
        .then(results => {
          if(!("error" in results)) {
            app.files = results
          } else {
            app.error = results.error
          }
        })
        .catch(err => {
          console.log(err)
        })
    }
  }
})

app.getBrowsableList(path='/');
