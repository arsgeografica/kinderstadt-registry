var _ = require('lodash'),
    browserify = require('browserify'),
    buffer = require('vinyl-buffer'),
    config = require('../config').code,
    gulp = require('gulp'),
    jshint = require('gulp-jshint'),
    logger = require('../util/bundleLogger'),
    plumber = require('gulp-plumber'),
    source = require('vinyl-source-stream'),
    sourcemaps = require('gulp-sourcemaps'),
    uglify = require('gulp-uglify'),
    watchify = require('watchify');


gulp.task('code', function(callback) {
    var pipeline = function(bundleConfig) {
        var outputName = bundleConfig.entries;
        _.extend(bundleConfig, {
            entries: './' + config.srcBase + '/' + bundleConfig.entries,
            debug: true });

        var bundler = browserify(bundleConfig);
        var bundle = function() {
            logger.start(bundleConfig.entries);

            var stream = bundler.bundle()
                .pipe(plumber())
                .pipe(source(outputName))
                .pipe(buffer());

            if(!global.isWatching) {
                stream.pipe(sourcemaps.init({ loadMaps: true }))
                    .pipe(uglify(config.uglify))
                    .pipe(sourcemaps.write('./'));
            }

            stream.pipe(gulp.dest(config.dst));
            logger.end(bundleConfig.entries);
        };

        if(global.isWatching) {
            logger.watch(bundleConfig.entries);

            bundler = watchify(bundler);
            bundler.on('update', bundle);
        }

        bundle();
    };

    config.bundles.forEach(pipeline);

    callback();
});
