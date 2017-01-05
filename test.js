  describe('Kernel', function() {

    it('should start a kernel', function(done) {
      window["@jupyterlab/services"].Kernel.startNew().then(function(kernel) {
        return kernel.shutdown();
      }).then(done, done);
    });

  });
