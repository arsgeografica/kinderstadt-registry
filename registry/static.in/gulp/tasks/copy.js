var _ = require('lodash'),
    config =require('../config').copy,
    gulp = require('gulp');


gulp.task('copy', function(callback) {
    _.forEach(config, function copy(config) {
        gulp.src(config.src)
            .pipe(gulp.dest(config.dst));
    });

    callback();
});
