var config = require('../config').jshint,
    gulp = require('gulp'),
    jshint = require('gulp-jshint');


gulp.task('jshint', function(callback) {
    gulp.src(config.src)
        .pipe(jshint())
        .pipe(jshint.reporter('jshint-stylish'));

    callback();
});
