<a name="readme-top"></a>
<!-- Presentation Block -->
<br />
<div align="center">
  <h2 align="center">BurningMop's qbittorrent search plugins collection</h2>
  <p align="center">
      A growing collection of search plugins for the qBittorrent, an awesome and opensource torrent client.
  </p>
  <br />
</div>

<!-- ToC -->

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#book-about-the-project">📖 About The Project</a>
    </li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#plugin-list">Plugin List</a></li>
    <li><a href="#developer-notes">Developer Notes</a></li>
    <li><a href="#dizzy-contributing">💫 Contributing</a></li>
    <li><a href="#handshake-support">🤝 Support</a></li>
    <li><a href="#warning-license">⚠️ License</a></li>
    <li><a href="#hammer_and_wrench-built-with">🛠️ Built With</a></li>
  </ol>
</details>

<!-- About Block -->

## :book: About The Project

This repository contains various search engine plugins that I developed for qBittorrent, an amazing and open source torrent client.

If you want to request a specific plugin or a existing one stops working, please let me know by opening an issue.

This repository it's inspired by [LightDestory](https://github.com/LightDestory/qBittorrent-Search-Plugins)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- Setup Block -->

## :gear: Installation

There are 2 ways to install unofficial plugins:

- The easier way is to copy the link of the "Download" table's column and use it as "web link" for qBittorrent.
- The other way is to save the file in a temporary location by going to the download link and saving the document as a **python file**, `.py`. Then you can install the plugin by selecting the file from your filesystem.

I intend to develop plugins that don't require any further configuration, and can be installed using method 1

Some plugins may need additional settings to work properly, please read carefully the _Notes_ section.

For any doubts about the installation process, please refer to the official wiki: [Install search plugins](https://github.com/qbittorrent/search-plugins/wiki/Install-search-plugins).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Plugin List

 To the best of my knowledge, all these plugins are working

| Search Engine                                                                                                                                        | Version | Last update | Download link                                                                                                 | Compatibility             |
|------------------------------------------------------------------------------------------------------------------------------------------------------|---------|-------------|---------------------------------------------------------------------------------------------------------------|---------------------------|
| [![Bit Search](https://www.google.com/s2/favicons?domain=bitsearch.to#.png) Bit Search](https://bitsearch.to/)                                       | 1.3     | 14/Jan/2026 | [Download](https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/main/bitsearch.py)         | qbt 5.1.x / python 3.12.x |
| [![calidadtorrent](https://www.google.com/s2/favicons?domain=calidadtorrent.com#.png) CalidadTorrent](https://calidadtorrent.com/)                   | 1.0     | 24/Nov/2024 | [Download](https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/main/calidadtorrent.py)    | qbt 5.0.x / python 3.9.x  |
| [![divxtotal](https://www.google.com/s2/favicons?domain=divxtotal.wtf#.png) divxtotal](https://divxtotal.wtf/)                                       | 1.0     | 07/Nov/2024 | [Download](https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/main/divxtotal.py)         | qbt 5.0.x / python 3.9.x  |
| [![dontorrent](https://www.google.com/s2/favicons?domain=dontorrent.equipment#.png) dontorrent](https://dontorrent.equipment/)                       | 1.2     | 14/Nov/2025 | [Download](https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/main/dontorrent.py)        | qbt 5.1.x / python 3.12.x |
| [![esmeraldatorrent](https://www.google.com/s2/favicons?domain=esmeraldatorrent.com#.png) esmeraldatorrent](https://esmeraldatorrent.com/)           | 1.0     | 07/Nov/2024 | [Download](https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/main/esmeraldatorrent.py)  | qbt 5.0.x / python 3.9.x  |
| [![My Porn Club](https://www.google.com/s2/favicons?domain=myporn.club#.png) My Porn Club](https://myporn.club/)                                     | 1.1     | 09/Nov/2024 | [Download](https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/main/mypornclub.py)        | qbt 4.6.x / python 3.9.x  |
| [![naranjatorrent](https://www.google.com/s2/favicons?domain=naranjatorrent.com#.png) naranjatorrent](https://naranjatorrent.com/)                   | 1.0     | 07/Nov/2024 | [Download](https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/main/naranjatorrent.py)    | qbt 5.0.x / python 3.9.x  |
| [![pediatorrent](https://www.google.com/s2/favicons?domain=pediatorrent.com#.png) pediatorrent](https://pediatorrent.com/)                           | 1.0     | 24/Nov/2024 | [Download](https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/main/pediatorrent.py)      | qbt 5.0.x / python 3.9.x  |
| [![PornRips.To](https://www.google.com/s2/favicons?domain=pornrips.to#.png) PornRips.To](https://pornrips.to/)                                       | 1.0     | 23/Nov/2025 | [Download](https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/main/pornrips.py)          | qbt 5.1.x / python 3.12.x |
| [![SolidTorrents.to](https://www.google.com/s2/favicons?domain=solidtorrents.to#.png) SolidTorrents.to](https://solidtorrents.to/)                   | 1.0     | 05/Jan/2024 | [Download](https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/main/solidtorrents.py)     | qbt 4.6.x / python 3.9.x  |
| [![The RarBg](https://www.google.com/s2/favicons?domain=therarbg.com#.png) The RarBg](https://therarbg.com/)                                         | 1.3     | 20/Oct/2024 | [Download](https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/main/therarbg.py)          | qbt 4.6.x / python 3.9.x  |
| [![TomaDivx](https://www.google.com/s2/favicons?domain=tomadivx.net#.png) TomaDivx](https://tomadivx.net/)                                           | 1.1     | 07/Nov/2024 | [Download](https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/main/tomadivx.py)          | qbt 5.0.x / python 3.9.x  |
| [![torrenflix](https://www.google.com/s2/favicons?domain=torrenflix.com#.png) Torrenflix](https://torrenflix.com/)                                   | 1.0     | 23/Nov/2024 | [Download](https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/main/torrenflix.py)        | qbt 5.0.x / python 3.9.x  |
| [![Torrent Downloads Pro](https://www.google.com/s2/favicons?domain=torrentdownloads.pro#.png) Torrent Downloads Pro](https://torrentdownloads.pro/) | 1.1     | 20/Oct/2024 | [Download](https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/main/torrentdownloads.py)  | qbt 4.6.x / python 3.9.x  |
| [![TrahT](https://www.google.com/s2/favicons?domain=traht.org#.png) TrahT](https://traht.org/)                                                       | 1.0     | 27/Dec/2023 | [Download](https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/main/traht.py)             | qbt 4.6.x / python 3.9.x  |
| [![XXXClub](https://www.google.com/s2/favicons?domain=xxxclub.to#.png) XXXClub](https://xxxclub.to/)                                                 | 1.3     | 29/Oct/2024 | [Download](https://raw.githubusercontent.com/BurningMop/qBittorrent-Search-Plugins/main/xxxclubto.py)         | qbt 5.0.x / python 3.9.x  |

 And I'm currently working on these plugins.

* [![Mac Torrents](https://www.google.com/s2/favicons?domain=torrentmac.net#.png) Mac Torrents](https://torrentmac.net/)
* [![BTDigg](https://www.google.com/s2/favicons?domain=btdig.com#.png) BTDigg](https://btdig.com/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Developer Notes

If you want to create a new search engine, please refer to the [official wiki](https://github.com/qbittorrent/search-plugins/wiki/How-to-write-a-search-plugin#python-class-file-structure)
and put it inside the root folder.

I have included the needed files requires to testing the plugins, the nova scripts with some modifications to easily debug in the nova3 folder.
While developing, put your engine file in `./nova3/engines` and then do:

1. `cd ./nova3`
2. `python ./nova2.py **search_engine** **category** **search keywords**`
 
<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- Contribute Block -->

## :dizzy: Contributing

If you are interested in contributing, feel free to open a PR

Thank you for considering contributing.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- Support Block -->

## :handshake: Support

 Donations are not really needed, and I do this just for fun and with lots of love. 

 If you insist, feel free to send crypto to `bc1qwxwzulc8at7txpc3m3x54jmylkheu3vpfptnfd` (BTC) or `0x34B4d628c6d06605D0B042b4287B7Ea1Eccfb654` (ETH) or give it to any charity of your choice in Burning Mop's name.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- License Block -->

## :warning: License

The content of this repository, except the nova scripts by qBittorrent devs, is distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- Built With Block -->

## :hammer_and_wrench: Built With

- [Python](https://www.python.org/)
- [Regex](https://en.wikipedia.org/wiki/Regular_expression)
- :heart:

<p align="right">(<a href="#readme-top">back to top</a>)</p>
