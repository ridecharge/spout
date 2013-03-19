            $(document).ready(function() {

                    var selectedDeviceType;
                    var selectedProduct;

                    $(".product-type").click(function() {

                        $.each($(".product-type"), function(key, elm) {
                            $(elm).removeClass("product-type-selected");
                        });

                        $(this).addClass("product-type-selected");
                        selectedDeviceType = $(this).text();
                        updateAppList();
                    });


                    $(".product-plus-button").click(function() {


                        var idString = "#" + $(this).attr("id");
                        var productCell = $.find(idString);
                        console.log(productCell);
                        console.log(productCell + $(this).attr("id"));
                        $.each($(".product-plus-button"), function(key, elm) {
                            if ($(elm).hasClass("product-name-selected") && $(elm) != $(this)) { //TODO make this collapse back into itself if it's already selected
                               $(elm).animate({
                                    height: 44
                                });
                               $(elm).removeClass("product-name-selected");
                            }
                        });

                        selectedProduct = $(this).attr('id');
                        if ($(productCell).hasClass("product-name-selected") == false){

                            $(productCell).addClass("product-name-selected");
                            $(productCell).animate({
                                height: 130 });
                            updateAppList($(productCell));
                        }
                    });

                    function updateAppList(product, tag, listArea) {

                        $tagRow = $(".tag-template").clone(true);  
                        $tagRow.removeClass("tag-template").addClass("tag");
                        $tagRow.removeAttr("style");

                        var appFilterPath = "/apps/filter?latest&tag=1";

                        if (selectedProduct != undefined) {
                            appFilterPath = appFilterPath + "&product=" + selectedProduct;
                        }
                        if (selectedDeviceType != undefined) {
                            appFilterPath = appFilterPath + "&device_type=" + selectedDeviceType;

                        }
                        $.getJSON(appFilterPath, '', function(data) {
                                console.log(data);
                                var app = data['apps'];
                                $tagRow.find("#app-itms-url").attr("href", app['url']);
                                var imgSrc = $tagRow.find("#app-icon").attr("src");
                                $tagRow.find("#app-name").text(app['name']);
                                var moreVersionsHref = $tagRow.find("#more-app-versions").attr("href")
                                $tagRow.find("#more-app-versions").attr("href",  moreVersionsHref + app['product'] + "device_type=" + app['device_type']);
                                $tagRow.find("#app-version").text(app['version']);
                                $tagRow.find("#app-refdate").text("updated " + app['refdate'] + " ago.");
                                $tagRow.find("#app-note").text(app['note']);
                            });

                        $(listArea).append($tagRow);

                    }

                    function updateAppTagList(listArea) {

                        $(".tag").remove();
                        var jsonPath = "/tags/filter?";
                        if(selectedProduct != undefined) {
                            jsonPath = jsonPath + "product=" + selectedProduct;
                        }
                        if (selectedDeviceType != undefined) {
                            jsonPath = jsonPath + "&device_type=" + selectedDeviceType;
                        }
                        console.log(jsonPath);
                        $.getJSON(jsonPath, '', function(data) { //get the tags for specified device type and product
                            $.each(data['tags'], function(key, value) {
                                var $tagRow;
                                $tagRow = $(".tag-template").clone(true);  
                                $tagRow.removeClass("tag-template").addClass("tag");
                                $tagRow.removeAttr("style");

                                var appFilterPath = "/apps/filter?latest&tag=" + value;

                                if (selectedProduct != undefined) {
                                    appFilterPath = appFilterPath + "&product=" + selectedProduct;
                                }
                                if (selectedDeviceType != undefined) {
                                    appFilterPath = appFilterPath + "&device_type=" + selectedDeviceType;
                                }

                                $.getJSON(appFilterPath, '', function(data) {
                                    console.log(data);
                                    var app = data['apps'];
                                    $tagRow.find("#app-itms-url").attr("href", app['url']);
                                    var imgSrc = $tagRow.find("#app-icon").attr("src");
                                    $tagRow.find("#app-name").text(app['name']);
                                    var moreVersionsHref = $tagRow.find("#more-app-versions").attr("href")
                                    $tagRow.find("#more-app-versions").attr("href",  moreVersionsHref + app['product'] + "device_type=" + app['device_type']);
                                    $tagRow.find("#app-version").text(app['version']);
                                    $tagRow.find("#app-refdate").text("updated " + app['refdate'] + " ago.");
                                    $tagRow.find("#app-note").text(app['note']);
                                });

                                $(listArea).append($tagRow);

                                });
                            });
                        }
                    }); 

        function appIconHrefGenerator(appUUID) {
            var href = "{{ MEDIA_URL }}" + appUUID + ".png";
            return href;
        }


