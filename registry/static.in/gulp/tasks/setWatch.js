var gulp = require('gulp');


gulp.task('setwatch', function(callback) {
    global.isWatching = true;

    callback();
});
