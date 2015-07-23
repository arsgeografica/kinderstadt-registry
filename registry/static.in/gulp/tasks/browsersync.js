var browsersync = require('browser-sync'),
    config = require('../config').browsersync,
    gulp = require('gulp');


gulp.task('browsersync', ['build'], function(callback) {
    browsersync(config);

    callback();
});
