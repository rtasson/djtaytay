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
      <source v-bind:src="'play?path=' + track.path" type="audio/webm" v-if="track">
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
          app.nextTrack();
        }
      }
    }
  }
})

Vue.component('file', {
  props: ['file'],
  template: `
    <li class="list-group-item">
      <div class="btn-group" role="group" aria-label="Song listing">
        <div class="btn-group" role="group">
          <a role="button" v-on:click="$emit('queue', file)">
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
    files: [],
    error: "",
    current_track_index: 0,
    queue: []
  },
  computed: {
    current_track: function () {
      if (this.queue.length > this.current_track_index) {
        return this.queue[this.current_track_index];
      } else {
        return;
      }
    },
    track_info: function () {
      if (this.queue.length > 0) {
        result = this.queue[this.current_track_index].title;
        result = result.concat(" by ");
        result = result.concat(this.queue[this.current_track_index].artist);
        return result;
      } else  {
        return "";
      }
    }
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
            this.files = results
          } else {
            this.error = results.error
          }
        })
        .catch(err => {
          console.log(err)
        })
    },
    playOrBrowse: function (file) {
      if (file.type == 'dir') {
        this.getBrowsableList(file.path)
      } else if (file.type == 'file') {
        this.queue = [file];
        this.current_track_index = 0;
      } else {
        this.error = "Unexpected type: " + file.type;
      }
    },
    queuePath: function (path) {
      this.queue.push(path)
    },
    nextTrack: function () {
      if ((this.current_track_index + 1) < this.queue.length) {
        this.current_track_index = this.current_track_index + 1;
      } else {
        this.current_track_index = 0
      }
    },
  }
})

app.getBrowsableList(path='/');
