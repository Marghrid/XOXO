<!DOCTYPE html>
<html lang="en">
<head>
  <title>XOXO configurations</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Merriweather" />
  <link rel="stylesheet" type="text/css" href="style.css" />
  <meta name="theme-color" content="#ffffff">
</head>

<body>
  <?php
    $dir   = "configs/";
    $files = scandir($dir);
    $files = array_diff(($files), array('.', '..'));
    $files = array_values($files);
    $json = json_encode($files);
    $num = count($files);
    echo "<h1>{$num} XOXO configurations </h1>";
  ?>

  <section>
    <div class=img-container id=xoxo-configs>
      <!-- <?php
        $chunks = array_chunk($files,21);
        $first_chunk = $chunks[0];
        print_r($first_chunk);
        foreach($first_chunk as $file) {
          echo "<a href=\"{$dir}{$file}\"><img src=\"{$dir}{$file}\"></a>";
        }
      ?> -->
    </div>
    <p id=info-text>DUMMYTEXT</p>
    <button type="button" onclick="load_some_more()">Load more</button>
  </section>

<script>
    show_num = 24
    function load_some_more() {
      let data = <?php echo $json; ?>;
      
      if( typeof load_some_more.counter == 'undefined' ) {
          load_some_more.counter = 0;
      } else {
        load_some_more.counter++;
      }
      div = document.getElementById('xoxo-configs');
      for (let i = load_some_more.counter*show_num; 
        i < (load_some_more.counter+1)*show_num && i < data.length; 
        ++i) {
        var a = document.createElement('a');
        var img = document.createElement('img');
        img.src = "configs/" + data[i];
        a.appendChild(img);
        a.href = "configs/" + data[i];
        div.appendChild(a);
      }
      p = document.getElementById("info-text");
      // todo: disable/remove "load more" button
      let num_configs = Math.min((load_some_more.counter+1)*show_num, data.length)
      p.innerHTML=`Showing ${num_configs} out of ${data.length} XOXO configurations.`;
    }
    load_some_more();
    console.log("Go away. Console is not for you.");
</script>
</body>
</html>
