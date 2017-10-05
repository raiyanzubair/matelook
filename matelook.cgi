#!/usr/bin/perl -w

# written by andrewt@cse.unsw.edu.au September 2016
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/matelook/
# Modified by Raiyan Zubair October 2016 for COMP2041 Assignment 2

###########>>>>>>>> I AM SORRY IF MY HTML LOOKS MESSY. I HAVE NEVER USED IT BEFORE AND HAVE NO IDEA WHAT IM MEANT TO INDENT. PLS DONT MARK DOWN. <<<<<<<<###########

use CGI qw/:all/;
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;
use CGI::Cookie;
use Time::Local;

sub main() {
    $users_dir = "dataset-medium";
    @users = sort(glob("$users_dir/*"));
    # print start of HTML ASAP to assist debugging if there is an error in the script
    
    # Now tell CGI::Carp to embed any warning in HTML
    warningsToBrowser(1);
    
   	# define some global variables
    $debug = 1;
    
    # Username, password, and logout parameters set in main instead of in the login subroutine, as that was the only way I could get cookies working...   	
    $username = param('username');
    $password = param('password');
    $logout = param('logout');
    
    # If the logout button is pressed then "delete cookies"
    if (defined $logout) {
        $cookie = CGI::Cookie->new(
                    -name=>'z3416387Login',
                    -path=>'/',
                    -value=>''
                    -expires=>'-1d');
    } 
    else {
        # COOKIE STUFF... basically puts cookies in the username and password parameters
        if ($ENV{'HTTP_COOKIE'} =~ /Login=(.*)&(.*)/) {
            $username = $1;
            $password = $2;
        }
    }
    print page_header();
    #subroutines for the various features. Improved readability
    reset_password();
	login();
    heading();
    search();
    #Only display the make post button if the profile is the profile is the one you logged in on
    if (param('profile_ID') == $login_ID) {
        make_post_button();
    }
    logout();
    user_page();
    matelist();
    my_posts();
    print page_trailer();
}

#
# Show unformatted details for user "profile_ID".
# Increment parameter profile_ID and store it as a hidden variable
#
sub user_page {
    $profile_ID = param('profile_ID') || 0;
    $user_to_show  = $users[$profile_ID % @users];
    $details_filename = "$user_to_show/user.txt";
    $default_img = "images/stockimg.jpg";

    # Getting the user information and formmating of it   
    open my $USERINFO, "$details_filename" or die "can not open $details_filename: $!";
    foreach $line (<$USERINFO>) {
        # Here the code checks for emails, passwords, and latitudes/longitudes and skips them
        if ($line =~ /^password.*/) {
            next;
        }
        if ($line =~ /^email.*/) {
            next;
        } 
        if ($line =~ /^home_l.*/) {
            next;
        }
        # Now it begins storing relevant user information
        if ($line =~ /^full_name=(.*)/) {
            $full_name = $1;             
        } 
        if ($line =~ /^program=(.*)/) {
            $program = $1;
        }
        if ($line =~ /^courses=\[(.*)\]/) {
            $courses = $1;
        }
        if ($line =~ /^birthday=(.*)/) {
            $birthday = $1;
        }
        if ($line =~ /^home_suburb=(.*)/) {
            $home_suburb = $1;
        }
        # matelist is obtained
        if ($line =~ /^mates=\[(.*)\]/) {
            $mates = $1;
            $mates =~ s/\s//g;
            @matelist = split(/,/, $mates);
        }
    }
    close $USERINFO;
    my $next_user = $profile_ID + 1;

#
# IN THIS SECTION USER INFORMATION IS ALL PRINTED OUT
#
    $whos_profile = "profile details";
    if (param('profile_ID') == $login_ID) {
        $whos_profile = "my profile";
    }
    print <<eof;
<div class=\"standard_heading\">
$whos_profile
</div>
<div class="matelook_user_details">
$full_name
<img class="profile_pic" src="$user_to_show/profile.jpg" onerror="if (this.src != '$default_img') this.src = '$default_img';">
eof

    print "Program: $program<br>";
    print "Birthday: $birthday<br>";
    # Only display information that was able to be extracted from user.txt
    if (defined $home_suburb) { 
        print "Suburb: $home_suburb<br>";
    }

# Next mate button   
    print <<eof;
</div>
</p>
<form>
<input type="hidden" name="profile_ID" value="$next_user">
<input type="submit" value="Next Mate" class="button">
</div>
<p>
</form>
eof
}



#
# HTML placed at the top of every page
#
sub page_header {
    
    return <<eof
Content-Type: text/html;charset=utf-8

<!DOCTYPE html>
<html lang="en">
<head>
<title>buttbook</title>
<link href="matelook.css" rel="stylesheet">
</head>
<body>
eof
}

#
# HTML placed at the bottom of every page
# It includes all supplied parameter values as a HTML comment
# if global variable $debug is set
#
sub page_trailer {
    my $html = "";
    $html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
    $html .= end_html;
    return $html;
}

################################                                            ################################ 
################################  ALL MY ADDITIONAL SUBROUTINES BEGIN HERE  ################################
################################                                            ################################

sub heading {
    $meme = "<a href=\"$ENV{'SCRIPT_NAME'}?profile_ID=$login_ID\">";
    if (defined $logout) {
        $meme = "";
    }
    print <<eof;
$meme
<div class="matelook_heading">
buttbook
</a>
</div>
eof
}

# login page that is an adapted version of work from previous labs
sub login {
    #if parameters are given open the directory and try and match the username and password
    if ($username && $password) {
        my $password_loc = "$users_dir/$username/user.txt";
        if (!open F, $password_loc) {   
            print start_form, "\n";
            print "Unknown username!\n";
            print submit(value => Retry), "\n";
            print end_form, "\n";
            exit;
        } else {
            foreach $line (<F>) {
                if ($line =~ /password=(.*)/) {
                    $realPass = $1;
                }
            }
            if ($password eq $realPass) {
                # If the password and username is correct a cookie is stored for those details
                # Those details are also stored as the login users details
                $cookie = CGI::Cookie->new(
                    -name=>'z3416387Login',
                    -value=>[$username, $password],
                    -expiry=>'+1s');
               
                print "<meta http-equiv=\"set-cookie\" content=\"$cookie\">";
                # The login_ID and login_username is stored so that the page title can be used as a link to the logged in users homepage
                $login_username = $username;
                $login_ID = 0;
                foreach $user (@users) {
                    if ($user =~ m/$login_username/) {
                        last;
                    }
                    $login_ID++;
                }
                $profile_ID = $login_ID;
            } else {
                print start_form, "\n";
                print "Incorrect password!\n";
                print submit(value => Retry), "\n";
                print end_form, "\n";
                exit;
            }
        }
    } elsif ($username) {
        print start_form, "\n";
        print hidden('username');
        print "Password:\n", textfield('password'), "\n";
        print submit(value => Login), "\n";
        print end_form, "\n";
        exit;
    } elsif ($password) {
        print start_form, "\n";
        print "Username:\n", textfield('username'), "\n";
        print hidden('username');
        print submit(value => Login), "\n";
        print end_form, "\n";
        exit;
    } else {
        print start_form, "\n";
        print "Username:\n", textfield('username'), "\n";
        print "Password:\n", textfield('password'), "\n";
        print submit(value => Login), "\n";
        print end_form, "\n";
        exit;
    }
}
 

#ALSO included in the login function is an option to have the password emailed to the user's specified email
sub reset_password {
    $zID_input = param('zID_input');
    $send_password = param('send_password');
    if (defined $send_password && $zID_input ne "") {
        open $RECOVER, "$users_dir/$zID_input/user.txt";    
        foreach $line (<$RECOVER>) {
            # Recover email address of user
            if ($line =~ /email=(.*)/) {
                $send_email = $1;
            }
            # Gets password of user
            if ($line =~ /password=(.*)/) {
                $password_to_send = $1;
            }
        }
        `echo "Greetings $zID_input, your password is $password_to_send" | mail -s "buttbook password reset" "$send_email" -c "raiyan.a.zubair\@gmail.com"`;
    }
    print "<div class=\"make_post_button\">";
    print <<eof;
<form>
Forgot your password? Type in your zID here: 
<input type="textfield" name ="zID_input">
<input type="submit" name="send_password" value="Reset Password" class="button">
</div>
<p>
</form>
</div>
eof

}

sub my_posts {
    # Here information about user profile_ID's posts and comments is obtained. 
    @posts  = sort(glob("$user_to_show/posts/*"));

    # push the directories of the page's mates posts as well into the array of posts we are going to examine.
    # Makes showing posts from mates very very easy. 
    foreach $mate (@matelist){
        @mate_posts = glob("$users_dir/$mate/posts/*");
        push (@posts, @mate_posts);
    }
    # Now go through each post from the user and their mates and obtain post information
    foreach $post (@posts) {
        open my $POSTS, "$post/post.txt" or die "can not open $post/post.txt: $!";
        foreach $line (<$POSTS>) { 
            # lines containing messages/time/zIDS are captured using regex and formatted for ease of reading
            # zID is converted to a name that is a link to profile of the person making the post
            # This process is repeated below for the comments and replies
            if ($line =~ /^from=(.*)/) {
                $temp_name =zIDtoName($1);
                $temp_index = zIDtoIndex($1);
                $post_from{$post} = "<a href=\"$ENV{'SCRIPT_NAME'}?profile_ID=$temp_index\">$temp_name</a>";

            } 
            if ($line =~ /^message=(.*)/) {
                $post_message{$post} =$1;
            }    
            if ($line =~ /^time=(.*)\+/) {
                #convert the post time to a sortable format and hash it
                $post_sort{$post} = total_seconds($1);   
                $post_time{$post} = $1;
                $post_time{$post} =~ s/T/ /;
             
            } 
        }
        close $POSTS;
        # Comment information for each individual post is obtained here and stored in a double hash 
        @comments = sort(glob("$post/comments/*"));
        foreach $comment (@comments) {
            open my $COMMENTS, "$comment/comment.txt" or die "can not open $comment/comment.txt: $!";
            foreach $line (<$COMMENTS>) {
                if ($line =~ /^from=(.*)/) {
                    $temp_name =zIDtoName($1);
                    $temp_index = zIDtoIndex($1);
                    $comment_from{$post}{$comment} = "<a href=\"$ENV{'SCRIPT_NAME'}?profile_ID=$temp_index\">$temp_name</a>";

                }
                if ($line =~ /^message=(.*)/) {
                    $comment_message{$post}{$comment} = $1;
                    # Now begins the part where I convert zIDs to links to the profile pages
                    # Firstly split the comment into an array of individual words and examine each looking for the zID fomat
                    @comment_string = split(" ", $comment_message{$post}{$comment});
                    foreach $comment_word (@comment_string) {
                        # If the word in the comment fits zID format (z9999999) get the name and index of the user using helper subroutines
                        if ($comment_word =~ /(z\d*)/){
                            $comment_name = zIDtoName($1);
                            $comment_index = zIDtoIndex($1);
                            $comment_word = "<a href=\"$ENV{'SCRIPT_NAME'}?profile_ID=$comment_index\">$comment_name</a>";
                        }
                    }
                    $comment_message{$post}{$comment} = join(" ", @comment_string);
                }    
                if ($line =~ /^time=(.*)\+/) {
                    $comment_sort{$post}{$comment} = total_seconds($1);
                    $comment_time{$post}{$comment} = $1;
                    $comment_time{$post}{$comment} =~ s/T/ /g;
                }
            }
            close $COMMENTS;
            # Reply information for comments is obtained here and put in a triple hash
            # Processes for getting info same as above except with triple hash
            @replies = sort(glob("$comment/replies/*"));
            foreach $reply (@replies) {
                open my $REPLIES, "$reply/reply.txt" or die "can not open $reply/reply.txt: $!";
                foreach $line (<$REPLIES>) {
                    if ($line =~ /^from=(.*)/) {
                        $temp_name =zIDtoName($1);
                        $temp_index = zIDtoIndex($1);
                        $reply_from{$post}{$comment}{$reply} = "<a href=\"$ENV{'SCRIPT_NAME'}?profile_ID=$temp_index\">$temp_name</a>";
                    }
                    if ($line =~ /^message=(.*)/) {
                        $reply_message{$post}{$comment}{$reply} = $1;
                        @reply_string = split(" ", $reply_message{$post}{$comment}{$reply});
                        foreach $reply_word (@reply_string) {
                            if ($reply_word =~ /(z\d*)/){
                                $reply_name = zIDtoName($1);
                                $reply_index = zIDtoIndex($1);
                                $reply_word = "<a href=\"$ENV{'SCRIPT_NAME'}?profile_ID=$reply_index\">$reply_name</a>";
                            }
                        }
                        $reply_message{$post}{$comment}{$reply} = join(" ", @reply_string);
                    }    
                    if ($line =~ /^time=(.*)\+/) {
                        $reply_sort{$post}{$comment}{$reply} = total_seconds($1);
                        $reply_time{$post}{$comment}{$reply} = $1;
                        $reply_time{$post}{$comment}{$reply} =~ s/T/ /g;
                    }
                }
                close $REPLIES;
            }
        }
    }

    # Now posts/comments/replies are displayed  
    print <<eof;
<div class=\"standard_heading\">
my posts
</div>
<div class=\"my_posts\">
eof
    # Go through each post of the user and if there is a message display it along with its time
    # Posts are sorted in reverse order by going through the special hash we used to store the time in hours
    foreach $post (sort {$post_sort{$b} <=> $post_sort{$a}} keys %post_sort) {
        if (defined $post_message{$post}) { 
            print "<div class=\"posts\">";
            # Replaces \n from text with HTML equivalent
            $post_message{$post} =~ s/\\n/<br>/g;            
            print "$post_from{$post}<br>";            
            print "$post_time{$post}<br>";
            print "$post_message{$post}<p><p>";
            # Now go through each comment for that post by 
            foreach $comment (sort {$comment_sort{$post}{$b} <=> $comment_sort{$post}{$a}} keys %{$comment_sort{$post}}) {      ##### <<<<<<!<!<!<!<! IT TOOK ME SO LONG TO FIND OUT THATS HOW YOU LOOP THROUGH DOUBLE HASHES.
                if (defined $comment_message{$post}{$comment}) {
                    print "<div class=\"comments\">";
                    $comment_message{$post}{$comment} =~ s/\\n/<br>/g;
                    print "$comment_from{$post}{$comment}--- ";
                    print "$comment_time{$post}{$comment}--- ";
                    print "$comment_message{$post}{$comment}<p>";
                    print "</div>";    
                }
                foreach $reply (sort keys %{$reply_sort{$post}{$comment}}) { 
                    if (defined $reply_message{$post}{$comment}{$reply}) {
                        print "<div class=\"replies\">";
                        $reply_message{$post}{$comment}{$reply} =~ s/\\n/<br>/g;
                        print "$reply_from{$post}{$comment}{$reply}--- ";
                        print "$reply_time{$post}{$comment}{$reply}--- ";
                        print "$reply_message{$post}{$comment}{$reply}<p>";    
                        print "</div>";
                    }
                }
             }
        print "</div>";    
        }
    }
    print "</div>";    
}

sub matelist {
    print <<eof;
<div class=\"standard_heading\">
matelist
</div>
<div class="matelist">
eof
    # Matelist array is created earlier in the user_info subroutine. Here it is being used to display the mate list.
    # Separated the code into various subroutines to hopefully improve readability. 
    foreach $mate (@matelist) {
        # Gets the profile picture of the mate
        $mate_pic = "$users_dir/$mate/profile.jpg";
        # Gets the name of the mate
        open my $MATE, "$users_dir/$mate/user.txt" or die "can not open: $!";
        foreach $line (<$MATE>) {
            if ($line =~ /^full_name=(.*)/) {
                $mate_name = $1;
            }
        }
        close $MATE;
        # Goes through $users_dir looking through zIDs till the mate is found. 
        $mate_ID = 0;
        foreach $user (@users) {
            # Increments mate_ID as it goes through the list of users. If the zID and mate match then
            # the loop ends and mate_ID is used in hyperlinking of images and student names
            if ($user =~ m/$mate/) {
                last;
            }
            $mate_ID++;
        }
        # Displays image and name of mate and makes them both hyperlinks to that mate's page
        print "<a href=\"$ENV{'SCRIPT_NAME'}?profile_ID=$mate_ID\">";
        print "<img class=\"small_pic\" src=\"$mate_pic\" onerror=\"if (this.src != '$default_img') this.src = '$default_img';\">\n";
        print "$mate_name\n\n";
        print "</a>";
    }
    print "</div>";
    print "<br>";
}

sub search {
    @users = sort(glob("$users_dir/*"));
    $default_img = "images/stockimg.jpg";
    print "<div class=\"search_bar\">";
    my $search = param('mate_search');
    my $search_index = 0;
    if (defined $search && $search ne "") {
        foreach my $user (@users) {
            # Goes through each user and checks if the search entry is a substring of the users name
            open my $SEARCH, "$user/user.txt" or die "can not open: $!";
            foreach $line (<$SEARCH>) {
                if ($line =~ /^full_name=(.*$search.*)/i) {
                    # From this the name, user picture, and search index is stored
                    $search_name{$user} = $1;
                    $search_pic{$user} = "$user/profile.jpg";
                    $search_ID{$user} = $search_index;
                }
            }
            close $SEARCH;
            $search_index++;
            #Now goes through all posts of users looking for the search term
            foreach $post (glob("$user/posts/*")) {
                open $SEARCHPOST, "$post/post.txt" or die;
                foreach $line (<$SEARCHPOST>) {
                    # stores time and who its from as temp variables
                    # Only properly stores them once the message matches with the search term
                    if ($line =~ /^from=(.*)/) {
                        $temp_name = $1;
                    }
                    if ($line =~ /^time=(.*)\+/) {
                        $temp_time = $1;
                    }
                    if ($line =~ /^message=(.*$search.*)/i) { 
                        $search_message{$user}{$post} = $1;
                        $search_message{$user}{$post} =~ s/\\n/<br>/g;
                        @search_string = split(" ", $search_message{$user}{$post});
                        #converts zIDs in string to links to profiles
                        foreach $search_word (@search_string) {
                            if ($search_word =~ /(z\d*)/){
                                $search_temp_name = zIDtoName($1);
                                $search_temp_index = zIDtoIndex($1);
                                $search_word = "<a href=\"$ENV{'SCRIPT_NAME'}?profile_ID=$search_temp_index\">$search_temp_name</a>";
                            }
                        }
                        $search_message{$user}{$post} = join(" ", @search_string);
                        $tempname1 = zIDtoName($temp_name);
                        $index1 = zIDtoIndex($temp_name);                        
                        $search_post_name{$user}{$post} = "<a href=\"$ENV{'SCRIPT_NAME'}?profile_ID=$index1\">$tempname1</a>";
                        $search_post_time{$user}{$post} = $temp_time;
                        $search_post_time{$user}{$post} =~ s/T/ /g;
                        $search_post_sort{$user}{$post} = total_seconds($temp_time)
                    }
                }
                close $SEARCHPOST;
            }
        }
        print <<eof;
<div class="standard_heading">
profile search results
</div>
<div class="search_name_results">
eof
        foreach $user (keys %search_name) {
           if (defined $search_name{$user}) {
                # Search index is used to link to the profile of the searched user
                print "<a href=\"$ENV{'SCRIPT_NAME'}?profile_ID=$search_ID{$user}\">";                
                print "<img class=\"small_pic\" src=\"$search_pic{$user}\" onerror=\"if (this.src != '$default_img') this.src = '$default_img';\">";
                print "$search_name{$user}\n";
                print "</a>";
            }
        }
        print <<eof;
</div>        
<div class="standard_heading">
post search results
</div>
<div class="search_name_results">
eof
        foreach $user (keys %search_message) {
            foreach $post (sort keys %{$search_post_sort{$user}}) {
                print "<div class=\"posts\">";
                print "$search_post_name{$user}{$post}<br>";
                print "$search_post_time{$user}{$post}<br>";
                print "$search_message{$user}{$post}<br>"; 
                print "</div>";
            }
        }
        print "</div>";
        exit;
    }
    print start_form, "\n";
    print textfield('mate_search'), "\n";
    print submit(value => "SEARCH"), "\n";
    print end_form, "\n";
    print "</div>";
}

sub make_post_button {
    $make_post = param('make_post');
    $post_contents = param('post_contents');

    # # Get the zID of the logged in profile
    $curr_zID = indextozID($login_ID);
    $curr_directory = $curr_zID;
    # Get the local time for the time of post
    ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time());
    # for some reason the localtime function displays 
    $year+=1900;
    $mon++;
    $curr_time = "$year-$mon-$mday\T$hour:$min:$sec+0000";
    if (defined $make_post) {
        @user_posts  = sort(glob("$curr_directory/posts/*"));
        # Go through the users post directory to find the total number of posts
        $post_index=0;
        foreach $user (@user_posts) {
            $post_index++;
        }
        # Make a new post directory that is not overwriting any old ones
        $new_post = "$curr_directory/posts/$post_index";
        mkdir $new_post;
        # print the post to post.txt and output it in the directory
        open ($POST, ">", "$curr_directory/posts/$post_index/post.txt");
        print $POST "from=$curr_zID\n";
        print $POST "time=$curr_time\n";
        print $POST "message=$post_contents\n";
        close $POST;
    }
    print "<div class=\"make_post_button\">";
    print <<eof;
<form>
<input type="textfield" name ="post_contents">
<input type="submit" name="make_post" value="Make a post" class="button">
</div>
<p>
</form>
</div>
eof

}

# Logout button
sub logout {
    print start_form, "\n";
    print submit(-name => "logout", -value => "logout"), "\n";
    print end_form, "\n";
}

################################   These are helper subroutines   ################################
################################   Help make code more legible    ################################
sub zIDtoName {
    ($zID) = @_;
    $student_name = $zID;
    foreach $user (@users) {
        if ($user =~ m/$zID/) {    
            open $PROFILE, "$user/user.txt";
            foreach $line (<$PROFILE>) {
                if ($line =~ /full_name=(.*)/) {
                    $student_name = $1;
                }
            }
            close $PROFILE; 
            last;
        }
    }
    return $student_name;
}

sub zIDtoIndex {
    ($zID) = @_;
    $index = 0;
    foreach $user (@users) {
        if ($user =~ m/$zID/) {
            last;
        }
        $index++; 
    }
    return $index;
}

sub indextozID {
    ($index_limit) = @_;
    $i = 0;
    foreach $user (@users) {
        $return_user = $user;
        if ($i == $index_limit) {
            last;
        }
        $i++;
    }
    return $return_user;
}

#converts an input time into total seconds so it can be sorted.
sub total_seconds {
    ($input_time) =  @_;
    $input_time =~ /(\d*)-(\d*)-(\d*)T(\d*):(\d*):(\d*)/;
    $year = $1;
    $month = $2;
    $day = $3;
    $hour = $4;
    $minute = $5;
    $second = $6;
    $total_seconds = 60*(60*(24*(365*$year+30*$month+$day)+$hour)+$minute)+$second;
    return $total_seconds;
}
main();
