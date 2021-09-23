<template>
  <div class="header">
    <div class="margins">
      <div class="row">
        <div class="title">joulehunter</div>
        <div class="metrics">
          <div class="metric-label">Duration:</div>
          <div class="metric-value">{{duration}} seconds</div>
          <div class="metric-label">Samples:</div>
          <div class="metric-value">{{session.sample_count}}</div>
          <div class="metric-label">Package:</div>
          <div class="metric-value">{{session.package}}</div>
          <div class="metric-label" v-if="session.component">Component:</div>
          <div class="metric-value" v-if="session.component">{{session.component}}</div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'Header',
  props: ['session'],
  computed: {
    duration() {
      return this.session.duration.toLocaleString(undefined, {maximumSignificantDigits: 3})
    }
  }
}
</script>
<style scoped>
.header {
  background: #292f32;
}
.row {
  display: flex;
  align-items: center;
}
.title {
  font-size: 34px;
  padding-top: 20px;
  padding-bottom: 16px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 10px;
  flex: 1;
}
.metrics {
  display: grid;
  grid-template-columns: auto auto auto auto;
  font-size: 14px;
  text-transform: uppercase;
  grid-gap: 1px 8px;
}

.metric-label {
  font-weight: 600;
  color: #a9abad;
}
.metric-value {
  color: #737779;
  margin-right: 0.5em;
}
</style>
