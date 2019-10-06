Vue.component('error', {
  props: ['message'],
  template: `
    <div id="error" class="alert alert-danger" role="alert" v-show="message">
      {{ message }}
    </div>
  `
})

Vue.component('player', {
  props: ['track'],
  template: `
    <audio controls class="player" preload="auto" v-on:loadstart="handlePlayer()">
      <source v-bind:src="'play?path=' + track" type="audio/webm" v-if="track">
    </audio>
  `,
  watch: {
    track: function (val) {
      var aud = document.querySelector("audio.player");
      aud.load();
    }
  },
  data: function () {
    return {
      handlePlayer: function () {
        var aud = document.querySelector("audio.player");
        aud.play();
        aud.onended = function() {
          app.shiftQueue();
        }
      }
    }
  }
})

Vue.component('file', {
  props: ['file'],
  template: `
           <li class="list-group-item">
              <div class="btn-group btn-group-justificed" role="group" aria-label="Song listing">
                <div class="btn-group" role="group">
                  <a role="button" v-on:click="$emit('queue', file.path)">
                    <button type="button" class="btn btn-default">queue</button>
                  </a>
                </div>
                <div class="btn-group">
                  <a role="button" v-on:click="$emit('play-or-browse', file)">
                    <button type="button" class="btn btn-default">{{ file.name }}</button>
                  </a>
                </div>
              </div>
           </li>
  `
})

var app = new Vue({
  el: 'div#app',
  data: {
    files: {},
    error: "",
    current_track: "",
    queue: []
  },
  methods: {
    getBrowsableList: function (path) {
      encodedPath = encodeURIComponent(path);
      fetch("browse?path=" + encodedPath,
        {credentials: 'same-origin', mode: 'same-origin', redirect: 'follow'}
        ).then(response => {
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
    },
    playOrBrowse: function (file) {
      if (file.type == 'dir') {
        app.getBrowsableList(file.path)
      } else if (file.type == 'file') {
        app.current_track = file.path;
      } else {
        app.error = "Unexpected type: " + file.type;
      }
    },
    queuePath: function (path) {
      app.queue.push(path)
    },
    shiftQueue: function () {
      if (app.queue.length != 0) {
        app.current_track = app.queue.shift();
      } else {
        app.current_track = ""
      }
    },
  }
})

app.getBrowsableList(path='/');
