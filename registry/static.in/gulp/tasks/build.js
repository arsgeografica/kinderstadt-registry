var gulp = require('gulp'),
    runSequence = require('run-sequence');


gulp.task('build', ['vendor'], function(callback) {
    runSequence(['styles', 'code', 'assets']);
    callback();
});
