<template>
  <div class="container" style="align-items: center">
    <!-- Errors -->
    <div v-if="errors && errors.length">
      <article class="message is-danger" align="center" v-bind:key="error" v-for="error of errors">
        <div class="message-header">
          <p>Error {{error.status}}</p>
          <button class="delete" aria-label="delete"></button>
        </div>
        <div class="message-body">{{error.data.message}}</div>
      </article>
    </div>

    <!-- Details content -->
    <div v-if="task && !errors.length">
      <h3 style="margin-top: 2%" class="title is-2">
          Task "{{ $route.params.task_id }}"
      </h3>
      <div align="center">
        <div class="card" align="left"
          v-bind:style="{ 'background': taskColorByStatus(task.status) }">
          <div class="card-content">
            <div class="columns">
              <div class="column" style="margin-left: 10px; border-right: 1px solid #c2c2c2;">
                <p class="title is-5">
                  {{task.status}}
                </p>
                <p>
                  <i style="margin-right: 8px"
                  class="fas text-muted" v-bind:class="iconByCategory(task.category)">
                  </i>
                  {{task.backend}}
                </p>
                <p>
                  <i style="margin-right: 8px" class="fas fa-list-ol"></i>
                  <b>{{task.jobs.length}}</b> jobs
                </p>
                <p>
                  <i style="margin-right: 8px" class="fas fa-calendar-alt text-muted"></i>
                  {{task.created_on | prettyDate}}
                </p>
              </div>
              <div class="column" style="margin-left: 10px;">
                <p>
                  Age: <b>{{task.age}}</b>
                </p>
                <p>
                  Scheduling:
                  <ul>
                    <li>Delay: <b>{{task.scheduling_cfg.delay}}</b></li>
                  </ul>
                  <ul>
                    <li>Max retries: <b>{{task.scheduling_cfg.max_retries}}</b></li>
                  </ul>
                </p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div v-if="task && !errors.length" style="margin-top: 20px" class="tabs">
      <ul>
        <li class="static" v-bind:class="{ 'is-active': (selected === 'jobs') }">
          <router-link v-on:click.native="selected = 'jobs'"
          :to="{path: '/tasks/' + $route.params.task_id }">
            Jobs
          </router-link>
        </li>
        <li class="static" v-if="selected === 'job_details'">
          <span class="icon"><i class="fas fa-angle-right fa-lg" aria-hidden="true"></i></span>
        </li>
        <li class="static" v-if="selected === 'job_details'"
        v-bind:class="{ 'is-active': (selected === 'job_details') }">
          <a>{{jobSelected.job_id}}</a>
        </li>
      </ul>
    </div>

    <!-- Jobs content -->
    <router-view></router-view>
    <div v-if="task && !errors.length && selected === 'jobs'">
      <ul>
        <li v-bind:key="job.job_id"
            v-for="job of task.jobs"
            style="width: 100%">
            <div class="card job-card" align="left"
            v-bind:style="{ 'background': jobColorByStatus(job.job_status) }">
              <div class="card-content">
                <router-link
                  :to="{path: '/tasks/' + $route.params.task_id + '/job/' + job.job_id }">
                  <div class="columns" v-on:click="openJobDetails(job)">
                    <div class="column" style="border-right: 1px solid #c2c2c2;">
                      {{job.job_status}}
                    </div>
                    <div class="column" style="margin-left: 10px;">
                      {{job.job_id}}
                    </div>
                  </div>
                </router-link>
              </div>
            </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Task',
  data: () => ({
    task: {},
    errors: [],
    selected: 'jobs',
    isActive: true,
    modalOpened: false,
    jobSelected: {},
    jobResult: {},
  }),
  created() {
    this.getTaskData(this.$route.params.task_id);
  },
  methods: {
    getTaskData(taskId) {
      axios
        .get(`/tasks/id/${taskId}`)
        .then((response) => {
          this.task = response.data;
          this.task.jobs = this.task.jobs.reverse();
        })
        .catch((e) => {
          this.errors.push(e.response);
        });
    },
    openJobDetails(job) {
      this.jobSelected = job;
      this.jobResult = job.result;
      this.selected = 'job_details';
    },
    taskColorByStatus(status) {
      if (status === 'COMPLETED') {
        return 'linear-gradient(to right,#39aa56 0,#39aa56 10px,#fff 10px,#fff 100%) no-repeat';
      } if (status === 'FAILED') {
        return 'linear-gradient(to right,red 0,red 10px,#fff 10px,#fff 100%) no-repeat';
      } if (status === 'ENQUEUED') {
        return 'linear-gradient(to right,gray 0,gray 10px,#fff 10px,#fff 100%) no-repeat';
      } if (status === 'RUNNING') {
        return 'linear-gradient(to right,#ffd21f 0,#ffd21f 10px,#fff 10px,#fff 100%) no-repeat';
      } if (status === 'SCHEDULED') {
        return 'linear-gradient(to right,#45b6f7 0,#45b6f7 10px,#fff 10px,#fff 100%) no-repeat';
      }
      return '';
    },
    jobColorByStatus(status) {
      if (status === 'finished') {
        return 'linear-gradient(to right,#39aa56 0,#39aa56 10px,#fff 10px,#fff 100%) no-repeat';
      } if (status === 'failed') {
        return 'linear-gradient(to right,red 0,red 10px,#fff 10px,#fff 100%) no-repeat';
      } if (status === 'queued') {
        return 'linear-gradient(to right,gray 0,gray 10px,#fff 10px,#fff 100%) no-repeat';
      } if (status === 'started') {
        return 'linear-gradient(to right,#ffd21f 0,#ffd21f 10px,#fff 10px,#fff 100%) no-repeat';
      }
      return '';
    },
    iconByCategory(category) {
      if (category === 'bug') {
        return 'fa-bug';
      } if (category === 'commit') {
        return 'fa-code-branch';
      }
      return '';
    },
  },
  watch: {
    // eslint-disable-next-line
    '$route.params.task_id': function (newId, oldId) {
      if (newId !== oldId) {
        this.getTaskData(newId);
      }
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1,
h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
article {
  width: 60%;
  margin-top: 20px;
  margin-left: auto;
  margin-right: auto;
}
.card {
  width: 100%;
}
.job-card {
  margin-bottom: 10px;
}
.job-card a {
 color: #4a4a4a !important;
}
</style>
